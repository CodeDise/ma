/**
 * Dwell-Time Countdown Timer & Direct Click Engine for Mio Ads
 * Requires 60-120 seconds dwell-time before impression counts,
 * unless user clicks ad directly (which immediately skips the timer).
 */

class DwellTimeTracker {
  constructor() {
    this.timerInterval = null;
    this.secondsRemaining = 60;
    this.totalDuration = 60;
    this.currentCampaignId = null;
    this.currentChannelId = null;
    this.hasCompleted = false;
  }

  initTimer(campaignId, channelId = null, durationSeconds = 60) {
    this.stopTimer();
    this.currentCampaignId = campaignId;
    this.currentChannelId = channelId;
    this.totalDuration = durationSeconds || 60;
    this.secondsRemaining = this.totalDuration;
    this.hasCompleted = false;

    this.updateDisplay();
    this.timerInterval = setInterval(() => {
      this.tick();
    }, 1000);
  }

  tick() {
    if (this.secondsRemaining > 0) {
      this.secondsRemaining--;
      this.updateDisplay();
    } else {
      this.onTimerComplete();
    }
  }

  updateDisplay() {
    const badge = document.getElementById("dwell-countdown-badge");
    const notice = document.getElementById("dwell-notice-text");
    if (badge) {
      const mins = Math.floor(this.secondsRemaining / 60);
      const secs = this.secondsRemaining % 60;
      badge.innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
    if (notice) {
      if (this.secondsRemaining > 0) {
        notice.innerText = `⏳ Stay for ${this.secondsRemaining}s or click directly to verify impression:`;
      } else {
        notice.innerText = "✅ Dwell-time verified! Impression recorded.";
      }
    }
  }

  async onTimerComplete() {
    this.stopTimer();
    this.hasCompleted = true;
    console.log("[DwellTimer] Completed naturally for campaign:", this.currentCampaignId);
    await this.reportImpression(false);
  }

  async clickAdDirectly() {
    // User clicks ad directly: bypass/skip timer immediately
    console.log("[DwellTimer] Direct click triggered! Bypassing timer for campaign:", this.currentCampaignId);
    this.stopTimer();
    const badge = document.getElementById("dwell-countdown-badge");
    const notice = document.getElementById("dwell-notice-text");
    if (badge) badge.innerText = "SKIPPED";
    if (notice) notice.innerText = "⚡ Direct click verified! Timer bypassed.";

    await this.reportImpression(true);
  }

  async reportImpression(clickedDirectly = false) {
    if (!this.currentCampaignId) return;

    try {
      const response = await fetch("/api/v1/ad/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: this.currentCampaignId,
          channel_id: this.currentChannelId,
          dwell_time_elapsed: this.totalDuration - this.secondsRemaining,
          clicked_directly: clickedDirectly
        })
      });
      const data = await response.json();
      console.log("[DwellTimer] Track result:", data);
      if (window.MioApp && window.MioApp.showToast) {
        window.MioApp.showToast(clickedDirectly ? "⚡ Direct Click Counted!" : "✅ Impression Verified!");
      }
    } catch (err) {
      console.error("[DwellTimer] Report error:", err);
    }
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }
}

window.dwellTracker = new DwellTimeTracker();
