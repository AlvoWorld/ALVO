"""
ALVO Platform - Performance Monitor
Real-time performance monitoring and metrics collection.
"""
import sqlite3
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Collects and reports performance metrics."""
    
    def __init__(self, db_path: str = "osya.db"):
        self.db_path = db_path
        self.metrics_history: List[Dict] = []
        self.max_history = 1000
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "database": self._get_database_metrics(),
            "system": self._get_system_metrics(),
            "queries": self._get_query_metrics(),
        }
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        return metrics
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database-specific metrics."""
        metrics = {}
        
        try:
            # File sizes
            if os.path.exists(self.db_path):
                metrics["size_mb"] = os.path.getsize(self.db_path) / 1024 / 1024
            
            wal_path = f"{self.db_path}-wal"
            if os.path.exists(wal_path):
                metrics["wal_size_mb"] = os.path.getsize(wal_path) / 1024 / 1024
            
            shm_path = f"{self.db_path}-shm"
            if os.path.exists(shm_path):
                metrics["shm_size_kb"] = os.path.getsize(shm_path) / 1024
            
            # Table statistics
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tables = ['agents', 'tasks', 'runs', 'messages', 'comments']
            table_stats = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_stats[table] = count
            
            metrics["tables"] = table_stats
            
            # Check for missing indexes
            missing_indexes = []
            foreign_keys = [
                ("runs", "agent_id"),
                ("runs", "task_id"),
                ("messages", "run_id"),
                ("tasks", "assignee_id"),
                ("comments", "task_id"),
            ]
            
            for table, column in foreign_keys:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='index' 
                    AND tbl_name='{table}' 
                    AND sql LIKE '%{column}%'
                """)
                if cursor.fetchone()[0] == 0:
                    missing_indexes.append(f"{table}.{column}")
            
            metrics["missing_indexes"] = missing_indexes
            
            # PRAGMA stats
            cursor.execute("PRAGMA cache_size")
            metrics["cache_size"] = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA journal_mode")
            metrics["journal_mode"] = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA synchronous")
            metrics["synchronous"] = cursor.fetchone()[0]
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        metrics = {}
        
        try:
            # Load average
            load1, load5, load15 = os.getloadavg()
            metrics["load_avg"] = {"1min": load1, "5min": load5, "15min": load15}
            
            # Memory (from /proc/meminfo)
            with open("/proc/meminfo") as f:
                meminfo = f.read()
            
            for line in meminfo.split("\n"):
                if "MemTotal:" in line:
                    metrics["mem_total_kb"] = int(line.split()[1])
                elif "MemAvailable:" in line:
                    metrics["mem_available_kb"] = int(line.split()[1])
                elif "SwapTotal:" in line:
                    metrics["swap_total_kb"] = int(line.split()[1])
                elif "SwapFree:" in line:
                    metrics["swap_free_kb"] = int(line.split()[1])
            
            if "mem_total_kb" in metrics and "mem_available_kb" in metrics:
                used = metrics["mem_total_kb"] - metrics["mem_available_kb"]
                metrics["mem_used_percent"] = round(used / metrics["mem_total_kb"] * 100, 1)
            
            # Disk usage
            stat = os.statvfs("/")
            metrics["disk_total_gb"] = round(stat.f_blocks * stat.f_frsize / 1024**3, 1)
            metrics["disk_free_gb"] = round(stat.f_bavail * stat.f_frsize / 1024**3, 1)
            metrics["disk_used_percent"] = round(
                (1 - stat.f_bavail / stat.f_blocks) * 100, 1
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def _get_query_metrics(self) -> Dict[str, Any]:
        """Benchmark common queries."""
        metrics = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            queries = {
                "count_agents": "SELECT COUNT(*) FROM agents",
                "list_agents": "SELECT * FROM agents ORDER BY name",
                "count_runs": "SELECT COUNT(*) FROM runs",
                "runs_with_agents": """
                    SELECT r.*, a.name 
                    FROM runs r 
                    LEFT JOIN agents a ON r.agent_id = a.id 
                    LIMIT 100
                """,
                "agent_stats": """
                    SELECT a.name, COUNT(r.id) as runs, SUM(r.cost_usd) as cost
                    FROM agents a 
                    LEFT JOIN runs r ON a.id = r.agent_id 
                    GROUP BY a.id
                """,
                "recent_messages": """
                    SELECT * FROM messages 
                    ORDER BY created_at DESC 
                    LIMIT 100
                """,
            }
            
            for name, query in queries.items():
                start = time.perf_counter()
                cursor.execute(query)
                cursor.fetchall()
                elapsed_ms = (time.perf_counter() - start) * 1000
                metrics[name] = round(elapsed_ms, 2)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error collecting query metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current performance."""
        metrics = self.collect_metrics()
        
        # Calculate health score (0-100)
        health_score = 100
        issues = []
        
        # Check system resources
        sys_metrics = metrics.get("system", {})
        if sys_metrics.get("mem_used_percent", 0) > 80:
            health_score -= 20
            issues.append("High memory usage")
        
        if sys_metrics.get("disk_used_percent", 0) > 80:
            health_score -= 20
            issues.append("High disk usage")
        
        if sys_metrics.get("load_avg", {}).get("1min", 0) > 2:
            health_score -= 15
            issues.append("High CPU load")
        
        # Check database
        db_metrics = metrics.get("database", {})
        if db_metrics.get("missing_indexes"):
            health_score -= 10
            issues.append(f"Missing indexes: {len(db_metrics['missing_indexes'])}")
        
        if db_metrics.get("wal_size_mb", 0) > 50:
            health_score -= 5
            issues.append("Large WAL file")
        
        # Check query performance
        query_metrics = metrics.get("queries", {})
        slow_queries = [k for k, v in query_metrics.items() if isinstance(v, (int, float)) and v > 100]
        if slow_queries:
            health_score -= 10
            issues.append(f"Slow queries: {', '.join(slow_queries)}")
        
        return {
            "health_score": max(0, health_score),
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
            "issues": issues,
            "metrics": metrics,
            "recommendations": self._get_recommendations(metrics, issues),
        }
    
    def _get_recommendations(self, metrics: Dict, issues: List[str]) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        db_metrics = metrics.get("database", {})
        
        if db_metrics.get("missing_indexes"):
            recommendations.append(
                "Add missing indexes: run 'python performance_monitor.py --add-indexes'"
            )
        
        if db_metrics.get("wal_size_mb", 0) > 50:
            recommendations.append("Run VACUUM to reclaim space")
        
        query_metrics = metrics.get("queries", {})
        if any(v > 100 for v in query_metrics.values() if isinstance(v, (int, float))):
            recommendations.append("Optimize slow queries or add indexes")
        
        sys_metrics = metrics.get("system", {})
        if sys_metrics.get("mem_used_percent", 0) > 70:
            recommendations.append("Consider increasing available memory")
        
        return recommendations
    
    def add_missing_indexes(self) -> List[str]:
        """Add missing database indexes."""
        added = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            indexes = [
                ("idx_runs_agent_id", "runs", "agent_id"),
                ("idx_runs_task_id", "runs", "task_id"),
                ("idx_messages_run_id", "messages", "run_id"),
                ("idx_tasks_assignee_id", "tasks", "assignee_id"),
                ("idx_comments_task_id", "comments", "task_id"),
                ("idx_runs_agent_status", "runs", "agent_id, status"),
                ("idx_messages_run_seq", "messages", "run_id, seq"),
                ("idx_tasks_status_assignee", "tasks", "status, assignee_id"),
            ]
            
            for index_name, table, columns in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns})")
                    added.append(f"{index_name} on {table}({columns})")
                    logger.info(f"Created index: {index_name}")
                except sqlite3.Error as e:
                    logger.error(f"Failed to create {index_name}: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding indexes: {e}")
        
        return added
    
    def export_metrics(self, output_path: str = "performance_metrics.json"):
        """Export metrics to JSON file."""
        metrics = self.collect_metrics()
        
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Metrics exported to {output_path}")
        return output_path


def main():
    """CLI interface for performance monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ALVO Performance Monitor")
    parser.add_argument("--db", default="osya.db", help="Database path")
    parser.add_argument("--summary", action="store_true", help="Show performance summary")
    parser.add_argument("--metrics", action="store_true", help="Show detailed metrics")
    parser.add_argument("--add-indexes", action="store_true", help="Add missing indexes")
    parser.add_argument("--export", help="Export metrics to file")
    parser.add_argument("--watch", type=int, help="Watch metrics every N seconds")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.db)
    
    if args.add_indexes:
        print("Adding missing indexes...")
        added = monitor.add_missing_indexes()
        for idx in added:
            print(f"  ✓ {idx}")
        print(f"\nAdded {len(added)} indexes")
    
    elif args.summary:
        summary = monitor.get_summary()
        print(f"\n{'='*60}")
        print(f"ALVO Platform Performance Summary")
        print(f"{'='*60}")
        print(f"Health Score: {summary['health_score']}/100")
        print(f"Status: {summary['status'].upper()}")
        
        if summary['issues']:
            print(f"\nIssues:")
            for issue in summary['issues']:
                print(f"  ⚠️  {issue}")
        
        if summary['recommendations']:
            print(f"\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  💡 {rec}")
        
        print(f"\nDatabase: {summary['metrics']['database'].get('size_mb', 0):.1f} MB")
        print(f"Memory Used: {summary['metrics']['system'].get('mem_used_percent', 0)}%")
        print(f"Disk Used: {summary['metrics']['system'].get('disk_used_percent', 0)}%")
    
    elif args.metrics:
        metrics = monitor.collect_metrics()
        print(json.dumps(metrics, indent=2))
    
    elif args.export:
        monitor.export_metrics(args.export)
        print(f"Metrics exported to {args.export}")
    
    elif args.watch:
        print(f"Watching metrics every {args.watch} seconds (Ctrl+C to stop)...")
        try:
            while True:
                summary = monitor.get_summary()
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Health: {summary['health_score']} | "
                      f"Load: {summary['metrics']['system'].get('load_avg', {}).get('1min', 0):.2f} | "
                      f"Mem: {summary['metrics']['system'].get('mem_used_percent', 0)}%", end="")
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
