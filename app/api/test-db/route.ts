import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

/**
 * Database Test Endpoint
 * GET /api/test-db
 * 
 * Verifies database connectivity and returns record counts for all main tables
 * Useful for:
 * - Testing Prisma connection
 * - Quick database overview
 * - Debugging connection issues
 */
export async function GET() {
  try {
    // Test database connection
    await prisma.$connect();
    
    // Count records in each main table
    const [
      usersCount,
      sportsCount,
      leaguesCount,
      teamsCount,
      matchesCount,
      predictionsCount,
      userStatsCount,
      teamStatsCount,
      matchStatisticsCount,
      matchAnalysisCount,
      dataSyncLogsCount,
    ] = await Promise.all([
      prisma.user.count(),
      prisma.sport.count(),
      prisma.league.count(),
      prisma.team.count(),
      prisma.match.count(),
      prisma.prediction.count(),
      prisma.userStats.count(),
      prisma.teamStats.count(),
      prisma.matchStatistics.count(),
      prisma.matchAnalysis.count(),
      prisma.dataSyncLog.count(),
    ]);

    // Calculate total records
    const totalRecords = 
      usersCount +
      sportsCount +
      leaguesCount +
      teamsCount +
      matchesCount +
      predictionsCount +
      userStatsCount +
      teamStatsCount +
      matchStatisticsCount +
      matchAnalysisCount +
      dataSyncLogsCount;

    return NextResponse.json({
      status: 'success',
      message: 'Database connection successful',
      data: {
        users: usersCount,
        sports: sportsCount,
        leagues: leaguesCount,
        teams: teamsCount,
        matches: matchesCount,
        predictions: predictionsCount,
        userStats: userStatsCount,
        teamStats: teamStatsCount,
        matchStatistics: matchStatisticsCount,
        matchAnalysis: matchAnalysisCount,
        dataSyncLogs: dataSyncLogsCount,
      },
      summary: {
        totalTables: 11,
        totalRecords,
        isEmpty: totalRecords === 0,
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Database connection error:', error);
    
    return NextResponse.json(
      {
        status: 'error',
        message: 'Database connection failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}