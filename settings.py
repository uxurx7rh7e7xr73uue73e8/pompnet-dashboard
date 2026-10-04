<audio id="click-sound" src="https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3" preload="auto"></audio>

<script>
  document.addEventListener("DOMContentLoaded", function () {
    const clickableElements = document.querySelectorAll('button, .btn, a, input[type="submit"], input[type="button"]');
    clickableElements.forEach(element => {
      element.addEventListener('click', () => {
        const sound = document.getElementById('click-sound');
        if (sound) {
          sound.currentTime = 0;
          sound.play().catch(error => {
            console.log("Audio play blocked by browser:", error);
          });
        }
      });
    });
  });
</script>
