document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('spinner').style.display = 'none';

  async function fetchData() {
    try {
      const response = await fetch('/data');
      const data = await response.json();

      const totalRequests = document.getElementById('totalRequests');
      const completedRequests = document.getElementById('completedRequests');
      const totalResources = document.getElementById('totalResources');

      if (totalRequests) totalRequests.textContent = data.requests.length;
      if (completedRequests) completedRequests.textContent = data.requests.filter(r => r.status === 'Completed').length;
      if (totalResources) totalResources.textContent = data.resources.length;
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }

  setInterval(fetchData, 5000);
  fetchData();

  const sosButton = document.getElementById('sosButton');
  const sosModal = document.getElementById('sosModal');
  const closeModal = document.getElementById('closeSOS');
  const locationSpan = document.getElementById('userLocation');
  const sirenAudio = document.getElementById('sirenAudio');

  if (sosButton) {
    sosButton.addEventListener('click', function () {
      sosModal.classList.remove('hidden');

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
          const coords = `Lat: ${position.coords.latitude.toFixed(5)}, Lon: ${position.coords.longitude.toFixed(5)}`;
          locationSpan.textContent = coords;
        }, () => {
          locationSpan.textContent = "Location access denied";
        });
      } else {
        locationSpan.textContent = "Geolocation not supported";
      }

      if (sirenAudio) {
        sirenAudio.play();
      }

      fetch('/notify_sos');
    });
  }

  if (closeModal) {
    closeModal.addEventListener('click', function () {
      sosModal.classList.add('hidden');
      if (sirenAudio) {
        sirenAudio.pause();
        sirenAudio.currentTime = 0;
      }
    });
  }

  if (Notification.permission !== 'granted') {
    Notification.requestPermission();
  }
});
