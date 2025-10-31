# API-FOOTBALL DATA → DATABASE TABLE MAPPING

## Quick reference guide for data integration - User requested data mapping to database schema

This document shows exactly which API-Football data goes into which database table and field.

---

## 📊 USER REQUESTED DATA MAPPING

### ⚡ CANLI SKOR VERİLERİ (Livescore Data)

| İstenen Veri | Veritabanı Tablosu | Alan Adı | API Endpoint |
|--------------|-------------------|----------|--------------|
| Anlık skor | `matches` | `homeScore`, `awayScore` | `/fixtures?live=all` |
| Dakika bilgisi | `matches` | `minute` | `/fixtures?live=all` |
| Maç durumu | `matches` | `status` | `/fixtures?live=all` |
| Ev sahibi golleri | `matches` | `homeScore` | `/fixtures?live=all` |
| Deplasman golleri | `matches` | `awayScore` | `/fixtures?live=all` |
| Yarı devre skorları | `matches` | `halfTimeHome`, `halfTimeAway` | `/fixtures?live=all` |

**Güncelleme Sıklığı**: 15 saniye  
**Cache TTL**: 15 saniye (canlı maçlar)

---

### 🎯 MAÇ OLAYLARI (Match Events)

| İstenen Veri | Veritabanı Tablosu | Alan Adı | API Endpoint |
|--------------|-------------------|----------|--------------|
| Goller (dakika, VAR) | `match_events` | `event_type='GOAL'`, `minute`, `var_decision` | `/fixtures/events?fixture={id}` |
| Sarı kartlar | `match_events` | `event_type='YELLOW_CARD'`, `player_name`, `minute`, `card_reason` | `/fixtures/events?fixture={id}` |
| Kırmızı kartlar | `match_events` | `event_type='RED_CARD'`, `player_name`, `minute`, `card_reason` | `/fixtures/events?fixture={id}` |
| Penaltılar | `match_events` | `event_type='PENALTY'`, `penalty_result` | `/fixtures/events?fixture={id}` |

**Güncelleme Sıklığı**: 15 saniye (canlı), sonrasında statik  
**Cache TTL**: 15 saniye (canlı), permanent (bitti)

**Event Types:**
```sql
'GOAL'           -- Gol atıldı
'YELLOW_CARD'    -- Sarı kart gösterildi
'RED_CARD'       -- Kırmızı kart gösterildi
'PENALTY'        -- Penaltı kazanıldı/kaçırıldı
'VAR'            -- VAR incelemesi
'SUBSTITUTION'   -- Oyuncu değişikliği (istenmedi ama API'den gelir)
```

**Query Examples:** See full document for detailed SQL queries.

---

### 📈 MAÇ İSTATİSTİKLERİ (Match Statistics)

#### Hücum İstatistikleri
- Şutlar: `homeTotalShots`, `awayShotsOnTarget`, `home_shots_off_target`, `home_shots_blocked`
- Gol Fırsatları: `home_goal_attempts`, `home_counter_attacks`, `home_dangerous_attacks`

#### Top Hakimiyeti
- Top hakimiyeti (%): `homePossession`, `awayPossession`

#### Set Piece İstatistikleri
- Köşe vuruşları: `homeCorners`, `awayCorners`
- Serbest vuruşlar: `home_free_kicks`, `away_free_kicks`
- Taçlar: `home_throw_ins`, `away_throw_ins`

#### Savunma İstatistikleri
- Fauller: `homeFouls`, `awayFouls`
- Ofsaytlar: `home_offsides`, `away_offsides`
- Kaleci kurtarışları: `home_goalkeeper_saves`, `away_goalkeeper_saves`

**Endpoint**: `/fixtures/statistics?fixture={id}`

---

### 📅 GENEL MAÇ VERİLERİ (General Match Data)

#### Fixtures & Results
All data stored in `matches` table:
- Maç programı, geçmiş sonuçlar
- Maç tarihi ve saati: `matchDate`, `kick_off_time`
- Sezon: `season_id` → `seasons`
- Hafta/round: `round`, `matchday`
- Stadyum: `venue_id` → `venues`
- Hakem: `referee_id` → `referees`
- Seyirci: `attendance`

#### Head to Head
`head_to_head` table:
- Geçmiş maçlar: `recent_results` (JSONB)
- İstatistikler: `team_1_wins`, `draws`, `team_2_wins`
- Gol ortalamaları: `avg_goals_per_match`

---

### 🏆 LİG VE TAKIM VERİLERİ

#### Standings (Puan Durumu)
`standings` table stores:
- Sıralama: `position`
- Maç istatistikleri: `matches_played`, `wins`, `draws`, `losses`
- Goller: `goals_for`, `goals_against`, `goal_difference`
- Puan: `points`
- Form: `form` (last 5 matches)

**Endpoint**: `/standings?league={id}&season={year}`

---

### 🎲 BAHİS VERİLERİ (Betting Odds)

`match_odds` table stores all betting data:

#### Pre-match Odds
- 1X2: `home_win_odds`, `draw_odds`, `away_win_odds`
- Alt/Üst: `over_2_5_odds`, `under_2_5_odds` (and 1.5, 3.5)
- BTTS: `btts_yes_odds`, `btts_no_odds`
- Handikap: `handicap_value`, `handicap_home_odds`
- Çifte şans: `home_or_draw_odds`, etc.

#### Live Odds
- Same fields with `odds_type='LIVE'`
- Tracked by `odds_timestamp`

**Endpoints**: 
- `/odds?fixture={id}` (pre-match)
- `/odds/live?fixture={id}` (live)

---

### 🤖 TAHMİN VERİLERİ (Predictions)

`match_predictions` table:

#### Win Probabilities
- `home_win_probability`, `draw_probability`, `away_win_probability`

#### Over/Under Predictions
- `over_2_5_probability`, `under_2_5_probability` (and 0.5, 1.5, 3.5, 4.5)

#### BTTS
- `btts_yes_probability`, `btts_no_probability`

#### Metadata
- `advice`: API recommendation
- `comparison_data`: Form, H2H analysis (JSONB)
- `confidence_score`: Overall confidence

**Endpoint**: `/predictions?fixture={id}`

---

### 📦 EK VERİLER (Additional Data)

#### Sakatlıklar ve Cezalar
`team_injuries` table:
- Tip: `type` ('INJURY', 'SUSPENSION', 'YELLOW_CARD_ACCUMULATION')
- Detaylar: `reason`, `severity`
- Tarihler: `start_date`, `expected_return_date`
- Ceza: `matches_suspended`, `matches_served`

**Endpoint**: `/injuries?league={id}&season={year}`

#### Kupalar
`team_trophies` table:
- Bilgiler: `competition_name`, `season`, `place`
- Tip: `trophy_type` ('LEAGUE', 'CUP', 'CONTINENTAL', 'WORLD')

**Endpoint**: `/trophies?team={id}`

---

## 🔄 VERİ AKIŞ ÖZETİ

### Real-time Updates (15 saniye)
1. **Canlı Maçlar**: `matches` (skor, dakika, durum)
2. **Maç Olayları**: `match_events` (gol, kart, VAR)
3. **Canlı Oranlar**: `match_odds` (odds_type='LIVE')

### Frequent Updates (1 saat)
1. **Gelecek Maçlar**: `matches` (fixtures)
2. **Pre-match Oranlar**: `match_odds` (odds_type='PRE_MATCH')
3. **Puan Durumu**: `standings`

### Daily Updates
1. **Sakatlıklar**: `team_injuries`
2. **Tahminler**: `match_predictions`

### Post-match Updates
1. **İstatistikler**: `match_statistics`
2. **Head to Head**: `head_to_head`

### Seasonal Updates
1. **Kupalar**: `team_trophies`
2. **Hakem İstatistikleri**: `referees`

---

## 📝 ÖRNEK KULLANIM SENARYOLARI

### Senaryo 1: Canlı Maç Takibi
Get live matches with scores and recent events - combines `matches` + `match_events`

### Senaryo 2: Maç Analizi Dashboard
Comprehensive match view - combines:
- `matches` (basic info)
- `match_statistics` (performance)
- `match_events` (timeline)
- `match_odds` (betting markets)
- `match_predictions` (AI analysis)

### Senaryo 3: Value Betting Fırsatları
Compare prediction probabilities with betting odds to find value bets:
- `match_predictions.over_2_5_probability`
- `match_odds.over_2_5_odds`
- Calculate: implied probability vs prediction probability

---

## ✅ ÖNEMLİ NOTLAR

1. **API Sync Priority**:
   - High (15s): Live matches, events
   - Medium (1h): Fixtures, odds, standings
   - Low (24h): Injuries, predictions, trophies

2. **Rate Limiting**:
   - Pro Plan: 7,500 requests/day = ~312/hour = ~5/minute
   - Batch requests when possible
   - Use caching aggressively

3. **Data Quality**:
   - Always store `rawData` JSONB for debugging
   - Track `last_updated` timestamps
   - Use API IDs for reconciliation

4. **Performance**:
   - Index all foreign keys
   - Use partial indexes for common queries
   - Consider materialized views for standings

5. **Scalability**:
   - Partition matches table by season
   - Archive old match_odds data
   - Use JSONB for flexible/changing data

---

## 🔗 RELATED DOCUMENTS

For full details, see:
- `API_FOOTBALL_PRO_SCHEMA.md` - Complete table definitions
- `API_FOOTBALL_PRO_ERD.md` - Visual database diagram

**Quick Access**: When starting a new conversation, say "veritabanı sema değişikliği" to retrieve these documents quickly.
