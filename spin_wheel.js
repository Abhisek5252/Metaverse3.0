class SpinWheel {
  constructor(canvasId, segments) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.segments = segments;
    this.radius = Math.min(this.canvas.width, this.canvas.height) / 2 * 0.9;
    this.center = {
      x: this.canvas.width / 2,
      y: this.canvas.height / 2
    };
    this.rotation = 0;
    this.isSpinning = false;
    this.draw();
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw segments
    const anglePerSegment = (Math.PI * 2) / this.segments.length;

    this.segments.forEach((segment, index) => {
      const startAngle = index * anglePerSegment + this.rotation;
      const endAngle = startAngle + anglePerSegment;

      this.ctx.beginPath();
      this.ctx.moveTo(this.center.x, this.center.y);
      this.ctx.arc(this.center.x, this.center.y, this.radius, startAngle, endAngle);
      this.ctx.closePath();

      this.ctx.fillStyle = segment.color;
      this.ctx.fill();
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      // Draw text
      this.ctx.save();
      this.ctx.translate(this.center.x, this.center.y);
      this.ctx.rotate(startAngle + anglePerSegment / 2);
      this.ctx.textAlign = 'right';
      this.ctx.fillStyle = '#ffffff';
      this.ctx.font = 'bold 16px Arial';
      this.ctx.fillText(segment.text, this.radius - 20, 6);
      this.ctx.restore();
    });

    // Draw center circle
    this.ctx.beginPath();
    this.ctx.arc(this.center.x, this.center.y, 20, 0, Math.PI * 2);
    this.ctx.fillStyle = '#ffffff';
    this.ctx.fill();
    this.ctx.strokeStyle = '#000000';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();

    // Draw pointer
    this.ctx.beginPath();
    this.ctx.moveTo(this.center.x - 20, this.center.y - this.radius - 10);
    this.ctx.lineTo(this.center.x + 20, this.center.y - this.radius - 10);
    this.ctx.lineTo(this.center.x, this.center.y - this.radius + 20);
    this.ctx.closePath();
    this.ctx.fillStyle = '#ff0000';
    this.ctx.fill();
  }

  spin() {
    return new Promise((resolve) => {
      if (this.isSpinning) return;
      this.isSpinning = true;

      // Keep improved spin animation
      const totalRotation = Math.PI * 2 * (10 + Math.random() * 5); // 10-15 full rotations
      const duration = 6; // seconds

      const startRotation = this.rotation;
      const startTime = Date.now();

      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        const progress = Math.min(elapsed / duration, 1);

        // Enhanced easing function for more realistic spin
        const easing = 1 - Math.pow(1 - progress, 4); // Quartic easing out
        this.rotation = startRotation + totalRotation * easing;

        this.draw();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          this.isSpinning = false;

          // Calculate winning segment
          const normalizedRotation = this.rotation % (Math.PI * 2);
          const segmentAngle = (Math.PI * 2) / this.segments.length;
          const winningIndex = Math.floor(normalizedRotation / segmentAngle);
          resolve(this.segments[winningIndex]);
        }
      };

      animate();
    });
  }
}