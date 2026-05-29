import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Robot parameters
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Farm Robot Telemetry Dashboard', fontsize=16, fontweight='bold')
fig.patch.set_facecolor('#1a1a2e')
for ax in [ax1, ax2, ax3]:
    ax.set_facecolor('#16213e')

# Data storage
time_data, rpm_data, battery_data = [], [], []
t = 0

def update(frame):
    global t
    t += 0.5

    # Simulated sensor data
    rpm = 60 + 20 * np.sin(t * 0.3) + np.random.normal(0, 2)
    battery = max(0, 100 - t * 0.8 + np.random.normal(0, 0.3))

    time_data.append(t)
    rpm_data.append(rpm)
    battery_data.append(battery)

    # Keep last 40 points
    if len(time_data) > 40:
        time_data.pop(0)
        rpm_data.pop(0)
        battery_data.pop(0)

    # Panel 1 - RPM vs Time
    ax1.clear()
    ax1.set_facecolor('#16213e')
    ax1.plot(time_data, rpm_data, color='#00ff88', linewidth=2)
    ax1.fill_between(time_data, rpm_data, alpha=0.2, color='#00ff88')
    ax1.set_title('Wheel RPM', color='white', fontsize=12)
    ax1.set_xlabel('Time (s)', color='white')
    ax1.set_ylabel('RPM', color='white')
    ax1.tick_params(colors='white')
    ax1.set_ylim(30, 100)
    ax1.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Max RPM')
    ax1.legend(facecolor='#1a1a2e', labelcolor='white')

    # Panel 2 - Battery %
    ax2.clear()
    ax2.set_facecolor('#16213e')
    color = '#00ff88' if battery > 50 else '#ffaa00' if battery > 20 else '#ff4444'
    ax2.plot(time_data, battery_data, color=color, linewidth=2)
    ax2.fill_between(time_data, battery_data, alpha=0.2, color=color)
    ax2.set_title('Battery Level', color='white', fontsize=12)
    ax2.set_xlabel('Time (s)', color='white')
    ax2.set_ylabel('Battery (%)', color='white')
    ax2.tick_params(colors='white')
    ax2.set_ylim(0, 105)
    ax2.axhline(y=20, color='red', linestyle='--', alpha=0.5, label='Low Battery')
    ax2.legend(facecolor='#1a1a2e', labelcolor='white')

    # Panel 3 - Torque vs Speed curve
    ax3.clear()
    ax3.set_facecolor('#16213e')
    speed = np.linspace(0, 120, 100)
    torque = 50 * (1 - (speed / 120) ** 1.5) + np.random.normal(0, 0.5, 100)
    ax3.plot(speed, torque, color='#ff6b6b', linewidth=2)
    ax3.axvline(x=rpm % 120, color='#00ff88', linestyle='--', 
                linewidth=1.5, label=f'Current: {rpm:.0f} RPM')
    ax3.set_title('Torque vs Speed', color='white', fontsize=12)
    ax3.set_xlabel('Speed (RPM)', color='white')
    ax3.set_ylabel('Torque (Nm)', color='white')
    ax3.tick_params(colors='white')
    ax3.set_ylim(0, 60)
    ax3.legend(facecolor='#1a1a2e', labelcolor='white')

    plt.tight_layout()

ani = animation.FuncAnimation(fig, update, interval=200, cache_frame_data=False)
plt.show()