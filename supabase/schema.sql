-- PrediBol shared backend groundwork (Supabase / PostgreSQL)
-- Run in Supabase SQL Editor only after creating the Supabase project.
-- Auth is required: this schema never accepts anonymous identities.

create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null check (char_length(trim(display_name)) between 2 and 24),
  avatar_url text,
  created_at timestamptz not null default now()
);

create table if not exists public.trivia_scores (
  id uuid primary key default gen_random_uuid(),
  player_id uuid not null references public.profiles(id) on delete cascade,
  points integer not null check (points between 1 and 100),
  category text not null,
  question_id text not null,
  created_at timestamptz not null default now()
);
create index if not exists trivia_scores_player_idx on public.trivia_scores(player_id);
create index if not exists trivia_scores_created_idx on public.trivia_scores(created_at desc);

create table if not exists public.polls (
  id uuid primary key default gen_random_uuid(),
  title text not null check (char_length(trim(title)) between 4 and 180),
  description text,
  options jsonb not null check (jsonb_typeof(options) = 'array' and jsonb_array_length(options) between 2 and 8),
  is_active boolean not null default true,
  closes_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.poll_votes (
  id uuid primary key default gen_random_uuid(),
  poll_id uuid not null references public.polls(id) on delete cascade,
  player_id uuid not null references public.profiles(id) on delete cascade,
  option_index integer not null check (option_index >= 0),
  created_at timestamptz not null default now(),
  unique (poll_id, player_id)
);
create index if not exists poll_votes_poll_idx on public.poll_votes(poll_id);

alter table public.profiles enable row level security;
alter table public.trivia_scores enable row level security;
alter table public.polls enable row level security;
alter table public.poll_votes enable row level security;

-- Public profile names for leaderboard; players can only edit their own profile.
drop policy if exists "Profiles are readable" on public.profiles;
create policy "Profiles are readable" on public.profiles for select to authenticated using (true);
drop policy if exists "Players create own profile" on public.profiles;
create policy "Players create own profile" on public.profiles for insert to authenticated with check (id = auth.uid());
drop policy if exists "Players update own profile" on public.profiles;
create policy "Players update own profile" on public.profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());

-- Score rows are private to their owner; leaderboard totals are exposed through a safe aggregate view below.
drop policy if exists "Players read own scores" on public.trivia_scores;
create policy "Players read own scores" on public.trivia_scores for select to authenticated using (player_id = auth.uid());
drop policy if exists "Players add own scores" on public.trivia_scores;
create policy "Players add own scores" on public.trivia_scores for insert to authenticated with check (player_id = auth.uid());

-- Polls can be read by signed-in users. Management is restricted to trusted server/admin work.
drop policy if exists "Authenticated read polls" on public.polls;
create policy "Authenticated read polls" on public.polls for select to authenticated using (true);

-- Players can read and cast only their own vote. Unique constraint prevents duplicate voting.
drop policy if exists "Players read own poll votes" on public.poll_votes;
create policy "Players read own poll votes" on public.poll_votes for select to authenticated using (player_id = auth.uid());
drop policy if exists "Players cast own vote" on public.poll_votes;
create policy "Players cast own vote" on public.poll_votes for insert to authenticated with check (player_id = auth.uid());

-- Aggregated totals without exposing individual vote choices.
create or replace view public.poll_results
with (security_invoker = true) as
select poll_id, option_index, count(*)::bigint as vote_count
from public.poll_votes
group by poll_id, option_index;

-- Public leaderboard totals, with display names and accumulated score.
create or replace view public.leaderboard
with (security_invoker = true) as
select p.id as player_id, p.display_name, coalesce(sum(s.points), 0)::bigint as total_points
from public.profiles p
left join public.trivia_scores s on s.player_id = p.id
group by p.id, p.display_name;

grant select on public.poll_results to authenticated;
grant select on public.leaderboard to authenticated;
