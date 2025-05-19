// scripts.js - Version simplifiée
document.addEventListener('DOMContentLoaded', () => {
  // Avatar preview for upload
  const avatarInput = document.getElementById('avatar');
  if (avatarInput) {
    avatarInput.addEventListener('change', function(e) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const img = document.querySelector('.rounded-circle');
        if (img) img.src = e.target.result;
      };
      if (e.target.files[0]) reader.readAsDataURL(e.target.files[0]);
    });
  }
});