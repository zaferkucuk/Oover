const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

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

  console.log('✅ Created leagues:', [premierLeague.name, laLiga.name].join(', '));

  // ============================================
  // PREMIER LEAGUE TEAMS
  // ============================================
  console.log('\n🏆 Creating Premier League teams...');

  const teams = [
    { name: 'Arsenal', shortName: 'ARS' },
    { name: 'Manchester City', shortName: 'MCI' },
    { name: 'Liverpool', shortName: 'LIV' },
    { name: 'Chelsea', shortName: 'CHE' },
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

  await prisma.match.create({
    data: {
      sportId: football.id,
      leagueId: premierLeague.id,
      homeTeamId: createdTeams[0].id,
      awayTeamId: createdTeams[1].id,
      matchDate: new Date('2025-11-01T15:00:00Z'),
      status: 'SCHEDULED',
      venue: 'Emirates Stadium',
    },
  });

  console.log('✅ Created match: Arsenal vs Manchester City');

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

  await prisma.userStats.upsert({
    where: { userId: testUser.id },
    update: {},
    create: {
      userId: testUser.id,
    },
  });

  await prisma.userSettings.upsert({
    where: { userId: testUser.id },
    update: {},
    create: {
      userId: testUser.id,
      favoriteSports: ['football'],
      favoriteLeagues: ['Premier League'],
    },
  });

  console.log('✅ Created test user:', testUser.email);

  // ============================================
  // SUMMARY
  // ============================================
  const [sportsCount, leaguesCount, teamsCount, matchesCount, usersCount] = await Promise.all([
    prisma.sport.count(),
    prisma.league.count(),
    prisma.team.count(),
    prisma.match.count(),
    prisma.user.count(),
  ]);

  console.log('\n📊 Seed Summary:');
  console.log('================');
  console.log(`✅ Sports: ${sportsCount}`);
  console.log(`✅ Leagues: ${leaguesCount}`);
  console.log(`✅ Teams: ${teamsCount}`);
  console.log(`✅ Matches: ${matchesCount}`);
  console.log(`✅ Users: ${usersCount}`);
  
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