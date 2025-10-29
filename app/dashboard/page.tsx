// Dashboard home page
// Main entry point for the dashboard with overview stats

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Globe, Trophy, Users, Calendar, BarChart3, TrendingUp } from 'lucide-react';

/**
 * Stat card component
 */
function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ElementType;
  trend?: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
        {trend && (
          <div className="mt-2 flex items-center text-xs text-green-600">
            <TrendingUp className="mr-1 h-3 w-3" />
            {trend}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Dashboard home page
 */
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome back! 👋</h1>
        <p className="text-muted-foreground">
          Here's what's happening with your sports predictions today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Countries"
          value="96"
          description="Active countries in database"
          icon={Globe}
        />
        <StatCard
          title="Leagues"
          value="0"
          description="Tracked leagues"
          icon={Trophy}
          trend="+0 this month"
        />
        <StatCard
          title="Teams"
          value="0"
          description="Total teams"
          icon={Users}
        />
        <StatCard
          title="Matches"
          value="0"
          description="Upcoming matches"
          icon={Calendar}
        />
        <StatCard
          title="Predictions"
          value="0"
          description="Active predictions"
          icon={BarChart3}
        />
        <StatCard
          title="Accuracy"
          value="0%"
          description="Prediction accuracy rate"
          icon={TrendingUp}
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Get started with these common tasks
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <a
            href="/dashboard/countries"
            className="flex flex-col items-center rounded-lg border p-4 transition-colors hover:bg-accent"
          >
            <Globe className="mb-2 h-8 w-8 text-primary" />
            <span className="font-medium">View Countries</span>
            <span className="text-xs text-muted-foreground">Browse all countries</span>
          </a>
          <a
            href="/dashboard/leagues"
            className="flex flex-col items-center rounded-lg border p-4 transition-colors hover:bg-accent"
          >
            <Trophy className="mb-2 h-8 w-8 text-primary" />
            <span className="font-medium">Manage Leagues</span>
            <span className="text-xs text-muted-foreground">Add or edit leagues</span>
          </a>
          <a
            href="/dashboard/teams"
            className="flex flex-col items-center rounded-lg border p-4 transition-colors hover:bg-accent"
          >
            <Users className="mb-2 h-8 w-8 text-primary" />
            <span className="font-medium">View Teams</span>
            <span className="text-xs text-muted-foreground">Browse all teams</span>
          </a>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest updates and changes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center">
              <div className="mr-4 rounded-full bg-primary/10 p-2">
                <Globe className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Countries database initialized</p>
                <p className="text-xs text-muted-foreground">96 countries added</p>
              </div>
              <span className="text-xs text-muted-foreground">Today</span>
            </div>
            
            <div className="flex items-center opacity-50">
              <div className="mr-4 rounded-full bg-muted p-2">
                <Trophy className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Leagues coming soon</p>
                <p className="text-xs text-muted-foreground">Feature in development</p>
              </div>
              <span className="text-xs text-muted-foreground">Pending</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}