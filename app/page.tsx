import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-foreground">
            🚀 shadcn/ui Setup Complete!
          </h1>
          <p className="text-muted-foreground">
            Testing Button component with all variants and sizes
          </p>
        </div>

        {/* Variants Section */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Button Variants</h2>
          <div className="flex flex-wrap gap-4">
            <Button>Default Button</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
        </div>

        {/* Sizes Section */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Button Sizes</h2>
          <div className="flex flex-wrap items-center gap-4">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">🎯</Button>
          </div>
        </div>

        {/* Disabled State */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Disabled State</h2>
          <div className="flex flex-wrap gap-4">
            <Button disabled>Disabled Default</Button>
            <Button variant="secondary" disabled>Disabled Secondary</Button>
            <Button variant="outline" disabled>Disabled Outline</Button>
          </div>
        </div>

        {/* Combinations */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Size + Variant Combinations</h2>
          <div className="flex flex-wrap gap-4">
            <Button variant="destructive" size="sm">Small Destructive</Button>
            <Button variant="outline" size="lg">Large Outline</Button>
            <Button variant="secondary" size="sm">Small Secondary</Button>
          </div>
        </div>

        {/* Dark Mode Test */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Dark Mode Test</h2>
          <p className="text-sm text-muted-foreground">
            💡 Change your system theme to see dark mode in action!
          </p>
          <div className="p-6 border border-border rounded-lg bg-card">
            <div className="flex flex-wrap gap-4">
              <Button>Works in Dark Mode</Button>
              <Button variant="secondary">Also Works</Button>
              <Button variant="outline">Outline Too</Button>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="mt-12 p-6 border border-border rounded-lg bg-muted/50">
          <h3 className="text-lg font-semibold mb-2">✅ Setup Status</h3>
          <ul className="space-y-1 text-sm text-muted-foreground">
            <li>✅ shadcn/ui dependencies installed</li>
            <li>✅ CSS variables configured (light + dark mode)</li>
            <li>✅ Button component working</li>
            <li>✅ Path aliases configured (@/)</li>
            <li>✅ TypeScript types working</li>
          </ul>
        </div>

      </div>
    </div>
  )
}
