import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

/**
 * Database Seed Script
 * 
 * Populates the database with initial data:
 * - Sports (Football, Basketball, Tennis)
 * - Sample leagues
 * - Sample teams
 * 
 * Run with: npx prisma db seed
 */

async function main() {
  console.log('🌱 Starting database seed...');

  // ============================================
  // SPORTS
  // ============================================
  console.log('\n📊 Creating sports...');
  
  const football = await prisma.sport.upsert({
    where: { slug: 'football' },
    update: {},
    create: {
      name: 'Football',
      slug: 'football',
      icon: '⚽',
      isActive: true,
      displayOrder: 1,
    },
  });

  const basketball = await prisma.sport.upsert({
    where: { slug: 'basketball' },
    update: {},
    create: {
      name: 'Basketball',
      slug: 'basketball',
      icon: '🏀',
      isActive: true,
      displayOrder: 2,
    },
  });

  const tennis = await prisma.sport.upsert({
    where: { slug: 'tennis' },
    update: {},
    create: {
      name: 'Tennis',
      slug: 'tennis',
      icon: '🎾',
      isActive: true,
      displayOrder: 3,
    },
  });

  console.log('✅ Created sports:', [football.name, basketball.name, tennis.name].join(', '));

  // ============================================
  // FOOTBALL LEAGUES
  // ============================================
  console.log('\n⚽ Creating football leagues...');

  const premierLeague = await prisma.league.upsert({
    where: { 
      sportId_name_season: {
        sportId: football.id,
        name: 'Premier League',
        season: '2024-2025',
      }
    },
    update: {},
    create: {
      sportId: football.id,
      name: 'Premier League',
      country: 'England',
      season: '2024-2025',
      externalId: 'pl-39',
      isActive: true,
    },
  });

  const laLiga = await prisma.league.upsert({
    where: { 
      sportId_name_season: {
        sportId: football.id,
        name: 'La Liga',
        season: '2024-2025',
      }
    },
    update: {},
    create: {
      sportId: football.id,
      name: 'La Liga',
      country: 'Spain',
      season: '2024-2025',
      externalId: 'll-140',
      isActive: true,
    },
  });

  const bundesliga = await prisma.league.upsert({
    where: { 
      sportId_name_season: {
        sportId: football.id,
        name: 'Bundesliga',
        season: '2024-2025',
      }
    },
    update: {},
    create: {
      sportId: football.id,
      name: 'Bundesliga',
      country: 'Germany',
      season: '2024-2025',
      externalId: 'bl-78',
      isActive: true,
    },
  });

  console.log('✅ Created leagues:', [
    premierLeague.name,
    laLiga.name,
    bundesliga.name,
  ].join(', '));

  // ============================================
  // PREMIER LEAGUE TEAMS
  // ============================================
  console.log('\n🏆 Creating Premier League teams...');

  const teams = [
    { name: 'Arsenal', shortName: 'ARS', externalId: 'team-42' },
    { name: 'Manchester City', shortName: 'MCI', externalId: 'team-50' },
    { name: 'Liverpool', shortName: 'LIV', externalId: 'team-40' },
    { name: 'Chelsea', shortName: 'CHE', externalId: 'team-49' },
    { name: 'Manchester United', shortName: 'MUN', externalId: 'team-33' },
    { name: 'Tottenham', shortName: 'TOT', externalId: 'team-47' },
  ];

  const createdTeams = [];
  for (const teamData of teams) {
    const team = await prisma.team.upsert({
      where: {
        leagueId_name: {
          leagueId: premierLeague.id,
          name: teamData.name,
        },
      },
      update: {},
      create: {
        leagueId: premierLeague.id,
        name: teamData.name,
        shortName: teamData.shortName,
        externalId: teamData.externalId,
        country: 'England',
      },
    });
    createdTeams.push(team);
  }

  console.log('✅ Created teams:', createdTeams.map(t => t.name).join(', '));

  // ============================================
  // SAMPLE MATCHES
  // ============================================
  console.log('\n⚽ Creating sample matches...');

  const match1 = await prisma.match.create({
    data: {
      sportId: football.id,
      leagueId: premierLeague.id,
      homeTeamId: createdTeams[0].id, // Arsenal
      awayTeamId: createdTeams[1].id, // Man City
      matchDate: new Date('2025-11-01T15:00:00Z'),
      status: 'SCHEDULED',
      venue: 'Emirates Stadium',
      round: 'Round 11',
    },
  });

  const match2 = await prisma.match.create({
    data: {
      sportId: football.id,
      leagueId: premierLeague.id,
      homeTeamId: createdTeams[2].id, // Liverpool
      awayTeamId: createdTeams[3].id, // Chelsea
      matchDate: new Date('2025-11-02T17:30:00Z'),
      status: 'SCHEDULED',
      venue: 'Anfield',
      round: 'Round 11',
    },
  });

  console.log('✅ Created matches:', [
    `${createdTeams[0].name} vs ${createdTeams[1].name}`,
    `${createdTeams[2].name} vs ${createdTeams[3].name}`,
  ].join(', '));

  // ============================================
  // TEST USER
  // ============================================
  console.log('\n👤 Creating test user...');

  const testUser = await prisma.user.upsert({
    where: { email: 'test@spre.app' },
    update: {},
    create: {
      email: 'test@spre.app',
      username: 'testuser',
      fullName: 'Test User',
      role: 'USER',
      isActive: true,
      emailVerified: true,
    },
  });

  // Create user stats
  await prisma.userStats.upsert({
    where: { userId: testUser.id },
    update: {},
    create: {
      userId: testUser.id,
      totalPredictions: 0,
      correctPredictions: 0,
      accuracy: 0,
      currentStreak: 0,
      longestStreak: 0,
      totalPoints: 0,
    },
  });

  // Create user settings
  await prisma.userSettings.upsert({
    where: { userId: testUser.id },
    update: {},
    create: {
      userId: testUser.id,
      theme: 'light',
      language: 'en',
      notificationsEnabled: true,
      emailNotifications: true,
      favoriteSports: ['football'],
      favoriteLeagues: ['Premier League'],
    },
  });

  console.log('✅ Created test user:', testUser.email);

  // ============================================
  // SUMMARY
  // ============================================
  console.log('\n📊 Seed Summary:');
  console.log('================');
  
  const counts = await Promise.all([
    prisma.sport.count(),
    prisma.league.count(),
    prisma.team.count(),
    prisma.match.count(),
    prisma.user.count(),
  ]);

  console.log(`✅ Sports: ${counts[0]}`);
  console.log(`✅ Leagues: ${counts[1]}`);
  console.log(`✅ Teams: ${counts[2]}`);
  console.log(`✅ Matches: ${counts[3]}`);
  console.log(`✅ Users: ${counts[4]}`);
  
  console.log('\n🎉 Database seed completed successfully!');
}

main()
  .catch((error) => {
    console.error('❌ Seed failed:', error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });