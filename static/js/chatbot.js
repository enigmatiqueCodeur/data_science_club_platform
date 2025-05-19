document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('chatbot-toggle');
  const win    = document.getElementById('chatbot-window');
  const msgs   = document.getElementById('chatbot-messages');
  const inp    = document.getElementById('chatbot-input');
  const btn    = document.getElementById('chatbot-send');

  // bascule l'affichage
  toggle.addEventListener('click', () => {
    win.classList.toggle('d-none');
    if (!win.classList.contains('d-none')) {
      inp.focus();
    }
  });

  // fonction fetch POST
  async function post(endpoint, payload) {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    return res.json();
  }

  // envoi du message
  btn.addEventListener('click', async () => {
    const text = inp.value.trim();
    if (!text) return;
    msgs.innerHTML += `<div><strong>Vous :</strong> ${text}</div>`;
    inp.value = '';
    let data;
    if (text.toLowerCase().startsWith('cherche ')) {
      const q = text.slice(7);
      data = await post('/chat/search_resources', {query: q});
      if (data.length) {
        msgs.innerHTML += `<div><em>Ressources trouvées :</em><ul>${
          data.map(r => `<li>${r.title}</li>`).join('')
        }</ul></div>`;
      } else {
        msgs.innerHTML += `<div><em>Aucune ressource pour « ${q} ».</em></div>`;
      }
    } else {
      data = await post('/chat/faq', {question: text});
      msgs.innerHTML += `<div><strong>Bot :</strong> ${data.answer}</div>`;
    }
    msgs.scrollTop = msgs.scrollHeight;
  });
});
