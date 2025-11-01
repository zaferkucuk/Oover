/**
 * Zod validation schemas for Supabase database tables
 * Generated on: 2025-11-01
 * 
 * These schemas provide runtime validation for database operations.
 * They align with the TypeScript types in database.types.ts but add
 * runtime validation logic for data integrity.
 */

import { z } from "zod";

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Match status enumeration
 */
export const MatchStatusSchema = z.enum([
  "SCHEDULED",
  "LIVE",
  "FINISHED",
  "POSTPONED",
  "CANCELLED",
]);

/**
 * Prediction outcome enumeration
 */
export const PredictionOutcomeSchema = z.enum(["HOME_WIN", "DRAW", "AWAY_WIN"]);

/**
 * User role enumeration
 */
export const UserRoleSchema = z.enum(["USER", "PREMIUM", "ADMIN"]);

// ============================================================================
// UPDATED TABLES (with new fields from Phase 2)
// ============================================================================

/**
 * Country schema - UPDATED with region and fifa_code
 * New fields added in backend_sync Phase 2
 */
export const CountrySchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  code: z.string().length(2).nullable().optional(),
  flag: z.string().nullable().optional(),
  flag_url: z.string().url().nullable().optional(),
  is_active: z.boolean().default(true),
  is_international: z.boolean().default(false),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime().nullable().optional(),
  // NEW FIELDS (Phase 2)
  region: z.string().max(50).nullable().optional(), // Geographic region (e.g., "Europe", "South America")
  fifa_code: z.string().length(3).nullable().optional(), // FIFA country code (e.g., "ENG", "GER")
});

export const CountryInsertSchema = CountrySchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  code: true,
  flag: true,
  flag_url: true,
  is_active: true,
  is_international: true,
  region: true,
  fifa_code: true,
});

export const CountryUpdateSchema = CountrySchema.omit({
  created_at: true,
}).partial();

/**
 * League schema - UPDATED with tier and confederation
 * New fields added in backend_sync Phase 2
 */
export const LeagueSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  sport_id: z.string().uuid(),
  country_id: z.string().uuid().nullable().optional(),
  code: z.string().max(50).nullable().optional(),
  external_id: z.string().max(100).nullable().optional(),
  logo: z.string().url().nullable().optional(),
  is_active: z.boolean().default(true),
  characteristics: z.record(z.any()).nullable().optional(), // JSONB
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  // NEW FIELDS (Phase 2)
  tier: z.number().int().positive().nullable().optional(), // League tier/division (1=top division)
  confederation: z.string().max(20).nullable().optional(), // UEFA, CONMEBOL, CONCACAF, etc.
});

export const LeagueInsertSchema = LeagueSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  country_id: true,
  code: true,
  external_id: true,
  logo: true,
  is_active: true,
  characteristics: true,
  tier: true,
  confederation: true,
});

export const LeagueUpdateSchema = LeagueSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

/**
 * Team schema - UPDATED with stadium and color fields
 * New fields added in backend_sync Phase 2
 */
export const TeamSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  code: z.string().max(50).nullable().optional(),
  country_id: z.string().uuid().nullable().optional(),
  external_id: z.string().max(100).nullable().optional(),
  founded: z.number().int().min(1800).max(2100).nullable().optional(),
  logo: z.string().url().nullable().optional(),
  website: z.string().url().nullable().optional(),
  market_value: z.number().nullable().optional(),
  is_active: z.boolean().nullable().default(true),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  // NEW FIELDS (Phase 2)
  stadium_name: z.string().max(200).nullable().optional(), // Home stadium name
  stadium_capacity: z.number().int().positive().nullable().optional(), // Stadium capacity
  primary_color: z.string().regex(/^#[0-9A-Fa-f]{6}$/).nullable().optional(), // Hex color (e.g., "#FF0000")
  secondary_color: z.string().regex(/^#[0-9A-Fa-f]{6}$/).nullable().optional(), // Hex color
});

export const TeamInsertSchema = TeamSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  code: true,
  country_id: true,
  external_id: true,
  founded: true,
  logo: true,
  website: true,
  market_value: true,
  is_active: true,
  stadium_name: true,
  stadium_capacity: true,
  primary_color: true,
  secondary_color: true,
});

export const TeamUpdateSchema = TeamSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

/**
 * Match schema - UPDATED with new fields
 * New fields added in database_update feature
 */
export const MatchSchema = z.object({
  id: z.string().uuid(),
  sport_id: z.string().uuid(),
  league_id: z.string().uuid(),
  home_team_id: z.string().uuid(),
  away_team_id: z.string().uuid(),
  match_date: z.string().datetime(),
  status: MatchStatusSchema.default("SCHEDULED"),
  home_score: z.number().int().min(0).nullable().optional(),
  away_score: z.number().int().min(0).nullable().optional(),
  half_time_home: z.number().int().min(0).nullable().optional(),
  half_time_away: z.number().int().min(0).nullable().optional(),
  external_id: z.string().max(100).nullable().optional(),
  round: z.string().max(50).nullable().optional(),
  stadium: z.string().max(200).nullable().optional(),
  attendance: z.number().int().min(0).nullable().optional(),
  raw_data: z.record(z.any()).nullable().optional(), // JSONB
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  last_synced_at: z.string().datetime().nullable().optional(),
  // NEW FIELDS (database_update)
  referee: z.string().max(200).nullable().optional(),
  referee_id: z.string().uuid().nullable().optional(),
  venue: z.string().max(200).nullable().optional(),
  venue_id: z.string().uuid().nullable().optional(),
});

export const MatchInsertSchema = MatchSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  status: true,
  home_score: true,
  away_score: true,
  half_time_home: true,
  half_time_away: true,
  external_id: true,
  round: true,
  stadium: true,
  attendance: true,
  raw_data: true,
  last_synced_at: true,
  referee: true,
  referee_id: true,
  venue: true,
  venue_id: true,
});

export const MatchUpdateSchema = MatchSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

/**
 * Standing schema - UPDATED with ppg field
 * New field added in database_update feature
 */
export const StandingSchema = z.object({
  id: z.string().uuid(),
  league_id: z.string().uuid().nullable().optional(),
  season_id: z.string().uuid().nullable().optional(),
  team_id: z.string().uuid().nullable().optional(),
  position: z.number().int().positive(),
  snapshot_date: z.string().datetime(),
  matches_played: z.number().int().min(0).nullable().optional(),
  wins: z.number().int().min(0).nullable().optional(),
  draws: z.number().int().min(0).nullable().optional(),
  losses: z.number().int().min(0).nullable().optional(),
  goals_for: z.number().int().min(0).nullable().optional(),
  goals_against: z.number().int().min(0).nullable().optional(),
  goal_difference: z.number().int().nullable().optional(),
  points: z.number().int().min(0).nullable().optional(),
  form: z.string().max(20).nullable().optional(), // e.g., "WWDLL"
  status: z.string().max(50).nullable().optional(), // e.g., "Champions League", "Relegation"
  home_wins: z.number().int().min(0).nullable().optional(),
  home_draws: z.number().int().min(0).nullable().optional(),
  home_losses: z.number().int().min(0).nullable().optional(),
  home_goals_for: z.number().int().min(0).nullable().optional(),
  home_goals_against: z.number().int().min(0).nullable().optional(),
  home_matches: z.number().int().min(0).nullable().optional(),
  away_wins: z.number().int().min(0).nullable().optional(),
  away_draws: z.number().int().min(0).nullable().optional(),
  away_losses: z.number().int().min(0).nullable().optional(),
  away_goals_for: z.number().int().min(0).nullable().optional(),
  away_goals_against: z.number().int().min(0).nullable().optional(),
  away_matches: z.number().int().min(0).nullable().optional(),
  round_number: z.number().int().positive().nullable().optional(),
  recent_form_points: z.number().int().min(0).nullable().optional(),
  created_at: z.string().datetime().nullable().optional(),
  updated_at: z.string().datetime().nullable().optional(),
  // NEW FIELD (database_update) - auto-calculated by trigger
  ppg: z.number().nullable().optional(), // Points per game
});

export const StandingInsertSchema = StandingSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
  ppg: true, // Auto-calculated, don't include in insert
}).partial({
  league_id: true,
  season_id: true,
  team_id: true,
  matches_played: true,
  wins: true,
  draws: true,
  losses: true,
  goals_for: true,
  goals_against: true,
  goal_difference: true,
  points: true,
  form: true,
  status: true,
  home_wins: true,
  home_draws: true,
  home_losses: true,
  home_goals_for: true,
  home_goals_against: true,
  home_matches: true,
  away_wins: true,
  away_draws: true,
  away_losses: true,
  away_goals_for: true,
  away_goals_against: true,
  away_matches: true,
  round_number: true,
  recent_form_points: true,
});

export const StandingUpdateSchema = StandingSchema.omit({
  created_at: true,
  updated_at: true,
  ppg: true, // Auto-calculated, don't include in update
}).partial();

/**
 * Match Event schema - UPDATED with new fields
 * New fields added in database_update feature
 */
export const MatchEventSchema = z.object({
  id: z.string().uuid(),
  match_id: z.string().uuid().nullable().optional(),
  team_id: z.string().uuid().nullable().optional(),
  event_type: z.string().max(50), // "GOAL", "CARD", "SUBSTITUTION", etc.
  event_time: z.number().int().min(0).max(120).nullable().optional(), // Minutes
  extra_time: z.number().int().min(0).max(30).nullable().optional(), // Extra time minutes
  player_name: z.string().max(200).nullable().optional(),
  event_details: z.record(z.any()).nullable().optional(), // JSONB for flexible event data
  external_id: z.string().max(100).nullable().optional(),
  created_at: z.string().datetime().nullable().optional(),
  updated_at: z.string().datetime().nullable().optional(),
  // NEW FIELDS (database_update)
  assist_player_id: z.string().uuid().nullable().optional(),
  assist_player_name: z.string().max(200).nullable().optional(),
  team_side: z.enum(["home", "away"]).nullable().optional(),
  goal_type: z.string().max(50).nullable().optional(), // "open_play", "penalty", "free_kick", etc.
  card_type: z.enum(["yellow", "red", "yellow_red"]).nullable().optional(),
  substitution_type: z.enum(["in", "out"]).nullable().optional(),
  score_home: z.number().int().min(0).nullable().optional(), // Score after event
  score_away: z.number().int().min(0).nullable().optional(), // Score after event
});

export const MatchEventInsertSchema = MatchEventSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  match_id: true,
  team_id: true,
  event_time: true,
  extra_time: true,
  player_name: true,
  event_details: true,
  external_id: true,
  assist_player_id: true,
  assist_player_name: true,
  team_side: true,
  goal_type: true,
  card_type: true,
  substitution_type: true,
  score_home: true,
  score_away: true,
});

export const MatchEventUpdateSchema = MatchEventSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

// ============================================================================
// NEW TABLES (added in backend_sync Phase 2)
// ============================================================================

/**
 * Team Statistics schema - NEW TABLE
 * Added in backend_sync Phase 2
 * 
 * Stores flexible team performance statistics using JSONB.
 * Can be used for season stats, match stats, or any aggregate period.
 */
export const TeamStatisticsSchema = z.object({
  id: z.string().uuid(),
  team_id: z.string().uuid(), // Required: which team
  league_id: z.string().uuid().nullable().optional(), // Optional: for league-specific stats
  season_id: z.string().uuid().nullable().optional(), // Optional: for season stats
  match_id: z.string().uuid().nullable().optional(), // Optional: for match-specific stats
  stat_type: z.string().max(50).nullable().optional(), // "season", "match", "aggregate", etc.
  statistics: z.record(z.any()), // JSONB: flexible statistics structure
  // Example structure:
  // {
  //   goals_for: 65,
  //   goals_against: 32,
  //   clean_sheets: 15,
  //   possession_avg: 58.5,
  //   pass_accuracy: 85.2,
  //   shots_per_game: 14.3,
  //   ...any other stats
  // }
  external_id: z.string().max(100).nullable().optional(),
  created_at: z.string().datetime().nullable().optional(),
  updated_at: z.string().datetime().nullable().optional(),
});

export const TeamStatisticsInsertSchema = TeamStatisticsSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  league_id: true,
  season_id: true,
  match_id: true,
  stat_type: true,
  external_id: true,
});

export const TeamStatisticsUpdateSchema = TeamStatisticsSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

/**
 * Team Statistics helper schemas for common statistical structures
 * These validate the JSONB statistics field for specific use cases
 */
export const SeasonStatisticsSchema = z.object({
  goals_for: z.number().int().min(0).optional(),
  goals_against: z.number().int().min(0).optional(),
  goal_difference: z.number().int().optional(),
  clean_sheets: z.number().int().min(0).optional(),
  matches_played: z.number().int().min(0).optional(),
  wins: z.number().int().min(0).optional(),
  draws: z.number().int().min(0).optional(),
  losses: z.number().int().min(0).optional(),
  average_possession: z.number().min(0).max(100).optional(),
  pass_accuracy: z.number().min(0).max(100).optional(),
  shots_per_game: z.number().min(0).optional(),
  shots_on_target_per_game: z.number().min(0).optional(),
  corners_per_game: z.number().min(0).optional(),
  fouls_per_game: z.number().min(0).optional(),
  yellow_cards: z.number().int().min(0).optional(),
  red_cards: z.number().int().min(0).optional(),
});

export const MatchStatisticsSchema = z.object({
  possession: z.number().min(0).max(100).optional(),
  total_shots: z.number().int().min(0).optional(),
  shots_on_target: z.number().int().min(0).optional(),
  corners: z.number().int().min(0).optional(),
  fouls: z.number().int().min(0).optional(),
  yellow_cards: z.number().int().min(0).optional(),
  red_cards: z.number().int().min(0).optional(),
  offsides: z.number().int().min(0).optional(),
  pass_accuracy: z.number().min(0).max(100).optional(),
  passes_completed: z.number().int().min(0).optional(),
  passes_attempted: z.number().int().min(0).optional(),
});

/**
 * Player Statistics schema - NEW TABLE
 * Added in backend_sync Phase 2
 * 
 * Stores flexible player performance statistics using JSONB.
 * Can be used for season stats, match stats, or any aggregate period.
 */
export const PlayerStatisticsSchema = z.object({
  id: z.string().uuid(),
  player_id: z.string().nullable().optional(), // External player ID (text, not UUID)
  player_name: z.string().max(200).nullable().optional(),
  player_position: z.string().max(50).nullable().optional(), // "Forward", "Midfielder", etc.
  team_id: z.string().uuid(), // Required: current/associated team
  league_id: z.string().uuid().nullable().optional(), // Optional: for league-specific stats
  season_id: z.string().uuid().nullable().optional(), // Optional: for season stats
  match_id: z.string().uuid().nullable().optional(), // Optional: for match-specific stats
  stat_type: z.string().max(50).nullable().optional(), // "season", "match", "aggregate", etc.
  statistics: z.record(z.any()), // JSONB: flexible statistics structure
  // Example structure:
  // {
  //   goals: 23,
  //   assists: 15,
  //   appearances: 34,
  //   minutes_played: 2890,
  //   yellow_cards: 5,
  //   red_cards: 0,
  //   rating: 7.8,
  //   ...any other stats
  // }
  external_id: z.string().max(100).nullable().optional(),
  created_at: z.string().datetime().nullable().optional(),
  updated_at: z.string().datetime().nullable().optional(),
});

export const PlayerStatisticsInsertSchema = PlayerStatisticsSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
}).partial({
  player_id: true,
  player_name: true,
  player_position: true,
  league_id: true,
  season_id: true,
  match_id: true,
  stat_type: true,
  external_id: true,
});

export const PlayerStatisticsUpdateSchema = PlayerStatisticsSchema.omit({
  created_at: true,
  updated_at: true,
}).partial();

/**
 * Player Statistics helper schemas for common statistical structures
 * These validate the JSONB statistics field for specific use cases
 */
export const PlayerSeasonStatisticsSchema = z.object({
  goals: z.number().int().min(0).optional(),
  assists: z.number().int().min(0).optional(),
  appearances: z.number().int().min(0).optional(),
  minutes_played: z.number().int().min(0).optional(),
  goals_per_match: z.number().min(0).optional(),
  minutes_per_goal: z.number().min(0).optional(),
  rating: z.number().min(0).max(10).optional(),
  yellow_cards: z.number().int().min(0).optional(),
  red_cards: z.number().int().min(0).optional(),
  substitutions_in: z.number().int().min(0).optional(),
  substitutions_out: z.number().int().min(0).optional(),
  shots_per_game: z.number().min(0).optional(),
  shots_on_target_per_game: z.number().min(0).optional(),
  pass_accuracy: z.number().min(0).max(100).optional(),
  key_passes: z.number().int().min(0).optional(),
  dribbles_completed: z.number().int().min(0).optional(),
  tackles: z.number().int().min(0).optional(),
  interceptions: z.number().int().min(0).optional(),
  clearances: z.number().int().min(0).optional(),
});

export const PlayerMatchStatisticsSchema = z.object({
  minutes_played: z.number().int().min(0).max(120).optional(),
  goals: z.number().int().min(0).optional(),
  assists: z.number().int().min(0).optional(),
  rating: z.number().min(0).max(10).optional(),
  shots: z.number().int().min(0).optional(),
  shots_on_target: z.number().int().min(0).optional(),
  passes_completed: z.number().int().min(0).optional(),
  passes_attempted: z.number().int().min(0).optional(),
  pass_accuracy: z.number().min(0).max(100).optional(),
  key_passes: z.number().int().min(0).optional(),
  dribbles_completed: z.number().int().min(0).optional(),
  dribbles_attempted: z.number().int().min(0).optional(),
  tackles: z.number().int().min(0).optional(),
  interceptions: z.number().int().min(0).optional(),
  fouls_committed: z.number().int().min(0).optional(),
  fouls_drawn: z.number().int().min(0).optional(),
  yellow_cards: z.number().int().min(0).max(2).optional(),
  red_cards: z.number().int().min(0).max(1).optional(),
});

// ============================================================================
// TYPE EXPORTS
// ============================================================================

// Country types
export type Country = z.infer<typeof CountrySchema>;
export type CountryInsert = z.infer<typeof CountryInsertSchema>;
export type CountryUpdate = z.infer<typeof CountryUpdateSchema>;

// League types
export type League = z.infer<typeof LeagueSchema>;
export type LeagueInsert = z.infer<typeof LeagueInsertSchema>;
export type LeagueUpdate = z.infer<typeof LeagueUpdateSchema>;

// Team types
export type Team = z.infer<typeof TeamSchema>;
export type TeamInsert = z.infer<typeof TeamInsertSchema>;
export type TeamUpdate = z.infer<typeof TeamUpdateSchema>;

// Match types
export type Match = z.infer<typeof MatchSchema>;
export type MatchInsert = z.infer<typeof MatchInsertSchema>;
export type MatchUpdate = z.infer<typeof MatchUpdateSchema>;

// Standing types
export type Standing = z.infer<typeof StandingSchema>;
export type StandingInsert = z.infer<typeof StandingInsertSchema>;
export type StandingUpdate = z.infer<typeof StandingUpdateSchema>;

// Match Event types
export type MatchEvent = z.infer<typeof MatchEventSchema>;
export type MatchEventInsert = z.infer<typeof MatchEventInsertSchema>;
export type MatchEventUpdate = z.infer<typeof MatchEventUpdateSchema>;

// Team Statistics types
export type TeamStatistics = z.infer<typeof TeamStatisticsSchema>;
export type TeamStatisticsInsert = z.infer<typeof TeamStatisticsInsertSchema>;
export type TeamStatisticsUpdate = z.infer<typeof TeamStatisticsUpdateSchema>;
export type SeasonStatistics = z.infer<typeof SeasonStatisticsSchema>;
export type MatchStatistics = z.infer<typeof MatchStatisticsSchema>;

// Player Statistics types
export type PlayerStatistics = z.infer<typeof PlayerStatisticsSchema>;
export type PlayerStatisticsInsert = z.infer<typeof PlayerStatisticsInsertSchema>;
export type PlayerStatisticsUpdate = z.infer<typeof PlayerStatisticsUpdateSchema>;
export type PlayerSeasonStatistics = z.infer<typeof PlayerSeasonStatisticsSchema>;
export type PlayerMatchStatistics = z.infer<typeof PlayerMatchStatisticsSchema>;

// Enum types
export type MatchStatus = z.infer<typeof MatchStatusSchema>;
export type PredictionOutcome = z.infer<typeof PredictionOutcomeSchema>;
export type UserRole = z.infer<typeof UserRoleSchema>;
