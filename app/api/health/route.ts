import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

/**
 * Health Check Endpoint
 * GET /api/health
 * 
 * Returns the health status of the application and its dependencies
 * Useful for monitoring, load balancers, and debugging
 */
export async function GET() {
  const startTime = Date.now();
  
  const checks = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    uptime: process.uptime(),
    database: {
      status: 'unknown',
      responseTime: 0,
    },
  };

  try {
    // Test database connection with a simple query
    const dbStartTime = Date.now();
    await prisma.$queryRaw`SELECT 1`;
    checks.database.responseTime = Date.now() - dbStartTime;
    checks.database.status = 'healthy';

    const totalResponseTime = Date.now() - startTime;

    return NextResponse.json({
      ...checks,
      totalResponseTime,
    });
  } catch (error) {
    console.error('Health check failed:', error);
    
    checks.status = 'unhealthy';
    checks.database.status = 'unhealthy';

    return NextResponse.json(
      {
        ...checks,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    );
  }
}