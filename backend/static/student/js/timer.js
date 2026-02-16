/**
 * Timer management for test sessions
 */

class Timer {
    constructor(expiresAt, onWarning, onExpire) {
        // Backend sends UTC datetime without timezone suffix
        // Append 'Z' so JavaScript knows it's UTC, not local time
        let dateStr = expiresAt;
        if (typeof dateStr === 'string' && !dateStr.endsWith('Z') && !dateStr.includes('+')) {
            dateStr += 'Z';
        }
        this.expiresAt = new Date(dateStr);
        this.onWarning = onWarning;
        this.onExpire = onExpire;
        this.warningShown = false;
        this.interval = null;
    }

    start() {
        this.update();
        this.interval = setInterval(() => this.update(), 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }

    update() {
        const now = new Date();
        const diff = this.expiresAt - now;

        if (diff <= 0) {
            this.stop();
            this.onExpire();
            return;
        }

        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        const display = `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        const timerElement = document.getElementById('timer');
        if (timerElement) {
            timerElement.textContent = display;
        }

        // Show warning when 10 minutes remaining
        if (diff <= 10 * 60 * 1000 && !this.warningShown) {
            this.warningShown = true;
            this.onWarning();
        }
    }
}

window.Timer = Timer;
