import matplotlib.pyplot as plt
import numpy as np

# Empirical Data from Bash Benchmark
profiles = ['No Adaptation', 'Retry', 'Select Reliable']
failure_rates = [100.0, 0.0, 0.0]  

# Comparative MTTR Data (OSGi Baseline vs. Spring Boot Mesh)
systems = ['OSGi Baseline\n(Shared Memory)', 'Distributed TAS\n(Reactive Network)']
mttr_values = [21.6, 53.0] 

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Distributed Failure Rates (Pf)
bars1 = ax1.bar(profiles, failure_rates, color=['#e74c3c', '#f1c40f', '#2ecc71'])
ax1.set_ylabel('Failure Rate (%)')
ax1.set_title('GoalD Distributed Execution: Failure Rate ($P_f$)')
ax1.set_ylim(0, 110)

# Plot 2: MTTR Comparison
bars2 = ax2.bar(systems, mttr_values, color=['#95a5a6', '#3498db'])
ax2.set_ylabel('Mean Time To Repair (ms)')
ax2.set_title('Self-Healing Latency: MTTR Comparison')

plt.tight_layout()
plt.savefig('goald_evaluation_metrics.png', dpi=300)
print(">> Metrics plotted successfully: goald_evaluation_metrics.png")