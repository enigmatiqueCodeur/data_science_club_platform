document.addEventListener('DOMContentLoaded', () => {
  // 1) CKEditor unique sur #editor-reply
  let replyEditor = null;
  const replyTextarea = document.querySelector('#editor-reply');
  if (replyTextarea) {
    ClassicEditor
      .create(replyTextarea)
      .then(editor => replyEditor = editor)
      .catch(console.error);
  }

  // 2) Envoyer la réponse
  const submitBtn = document.getElementById('submit-reply');
  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      if (replyEditor) replyEditor.updateSourceElement();
      document.getElementById('reply-form').submit();
    });
  }

  // 3) Répondre à un post (scroll + parent_id)
  document.querySelectorAll('.reply-btn').forEach(btn => {
    btn.setAttribute('type', 'button');
    btn.addEventListener('click', () => {
      const pid = btn.dataset.parent;
      const parentInput = document.getElementById('parent_id');
      if (parentInput) parentInput.value = pid;
      document.getElementById('reply-form')
              .scrollIntoView({ behavior: 'smooth', block: 'center' });
      if (replyEditor) replyEditor.editing.view.focus();
    });
  });

  // 4) Like / Unlike
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.setAttribute('type', 'button');
    btn.addEventListener('click', async e => {
      e.preventDefault();
      const postId = btn.dataset.postId;
      try {
        const res  = await fetch(`/forum/post/${postId}/like`, { method: 'POST' });
        const data = await res.json();
        btn.querySelector('.like-count').textContent = data.count;
        btn.classList.toggle('btn-secondary', data.action === 'like');
        btn.classList.toggle('btn-outline-secondary', data.action !== 'like');
      } catch (err) {
        console.error('Like error', err);
      }
    });
  });

  // 5) Mentions (@username, @all)
  let suggestionBox = null;
  if (replyTextarea) {
    replyTextarea.addEventListener('input', async e => {
      const text = e.target.value;
      const last = text.match(/\S+$/)?.[0] || '';
      if (!last.startsWith('@')) {
        suggestionBox?.remove();
        suggestionBox = null;
        return;
      }
      const query = last.slice(1);
      const users = await fetch(`/forum/users?q=${encodeURIComponent(query)}`)
                         .then(r => r.json());
      if (!users.length && query !== 'all') return;
      suggestionBox?.remove();
      suggestionBox = document.createElement('div');
      suggestionBox.className = 'suggestion-box';
      Object.assign(suggestionBox.style, {
        position: 'absolute', background: '#fff',
        border: '1px solid #ccc', zIndex: '1000',
        maxHeight: '150px', overflowY: 'auto'
      });
      // @all
      const allOpt = document.createElement('div');
      allOpt.className = 'suggestion-item';
      allOpt.textContent = '@all';
      allOpt.addEventListener('click', () => {
        replyTextarea.value = text.replace(/@\S*$/, '@all ');
        suggestionBox.remove();
        replyTextarea.focus();
      });
      suggestionBox.appendChild(allOpt);
      // utilisateurs
      users.forEach(u => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = `@${u.username}`;
        item.addEventListener('click', () => {
          replyTextarea.value = text.replace(/@\S*$/, `@${u.username} `);
          suggestionBox.remove();
          replyTextarea.focus();
        });
        suggestionBox.appendChild(item);
      });
      const rect = replyTextarea.getBoundingClientRect();
      suggestionBox.style.top  = `${rect.bottom + window.scrollY}px`;
      suggestionBox.style.left = `${rect.left   + window.scrollX}px`;
      document.body.appendChild(suggestionBox);
    });
    document.addEventListener('click', e => {
      if (suggestionBox 
          && !replyTextarea.contains(e.target) 
          && !suggestionBox.contains(e.target)) {
        suggestionBox.remove();
        suggestionBox = null;
      }
    });
  }

  // 6) Modale avatar
  document.querySelectorAll('.avatar-clickable').forEach(img => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', () => {
      const modalEl  = document.getElementById('avatarModal');
      const modalImg = document.getElementById('avatarModalImage');
      modalImg.src = img.src;
      new bootstrap.Modal(modalEl).show();
    });
  });
});
