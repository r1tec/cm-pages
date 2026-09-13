// Comportamentos da BPV preservados sem o runtime de React/TanStack.
(function () {
  var params = new URLSearchParams(window.location.search);
  if (params.size) {
    document.querySelectorAll('a[href]').forEach(function (link) {
      var url = new URL(link.getAttribute('href'), window.location.href);
      if (url.protocol !== 'https:' && url.protocol !== 'http:') return;
      params.forEach(function (value, key) {
        if (!url.searchParams.has(key)) url.searchParams.set(key, value);
      });
      link.href = url.toString();
    });
  }
  document.querySelectorAll('.video-poster[data-video-id]').forEach(function (button) {
    button.addEventListener('click', function () {
      var video = document.createElement('video');
      video.setAttribute('aria-label', button.getAttribute('aria-label'));
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      video.preload = 'metadata';
      video.src = 'https://storage.googleapis.com/msgsndr/sJwwUNFpd1tYVdbwmA3f/media/' + button.dataset.videoId + '.mp4';
      button.replaceWith(video);
    }, { once: true });
  });
})();
