import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Bot, CheckSquare, Sparkles, ArrowRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const features = [
  { icon: Bot, title: "AI Chat Assistant", desc: "Get smart task suggestions and help from your personal AI sidebar." },
  { icon: CheckSquare, title: "Task Management", desc: "Create, organize, and track tasks with priorities and filters." },
  { icon: Sparkles, title: "Smart Organization", desc: "Let AI help you prioritize and stay productive effortlessly." },
];

export default function Landing() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="fixed top-0 z-50 w-full glass">
        <div className="container flex h-16 items-center justify-between">
          <h1 className="font-display text-xl font-bold text-gradient">AI TODO</h1>
          <div className="flex gap-3">
            {user ? (
              <Button asChild><Link to="/dashboard">Dashboard</Link></Button>
            ) : (
              <>
                <Button variant="ghost" asChild><Link to="/login">Log in</Link></Button>
                <Button asChild><Link to="/signup">Get Started</Link></Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="container flex min-h-screen flex-col items-center justify-center pt-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="max-w-3xl"
        >
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm text-primary">
            <Sparkles className="h-4 w-4" /> Powered by AI
          </div>
          <h1 className="font-display text-5xl font-bold leading-tight tracking-tight md:text-7xl">
            Your tasks,{" "}
            <span className="text-gradient">supercharged</span>{" "}
            with AI
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
            Manage your to-do list with an intelligent AI assistant that helps you stay focused, organized, and productive.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            {user ? (
              <Button size="lg" asChild className="gap-2 glow">
                <Link to="/dashboard">Go to Dashboard <ArrowRight className="h-4 w-4" /></Link>
              </Button>
            ) : (
              <>
                <Button size="lg" asChild className="gap-2 glow">
                  <Link to="/signup">Start for Free <ArrowRight className="h-4 w-4" /></Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="/login">Log in</Link>
                </Button>
              </>
            )}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-32 grid w-full max-w-4xl gap-6 md:grid-cols-3"
        >
          {features.map((f) => (
            <div key={f.title} className="glass rounded-xl p-6 text-left transition-all hover:glow">
              <f.icon className="mb-4 h-8 w-8 text-primary" />
              <h3 className="font-display text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
