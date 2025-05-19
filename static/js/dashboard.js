document.addEventListener('DOMContentLoaded', () => {
  // helper pour fetch + JSON
  async function loadJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${url} → ${res.status}`);
    return res.json();
  }

  // 1) Metrics (views / downloads / durations)
  loadJSON('/dashboard/metrics')
    .then(data => {
      const ctx = document.getElementById('activityChart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [
            {
              label: 'Vues',
              data: data.views,
              borderWidth: 2,
              fill: false,
              tension: 0.3
            },
            {
              label: 'Téléchargements',
              data: data.downloads,
              borderWidth: 2,
              fill: false,
              tension: 0.3
            },
            {
              label: 'Durée moyenne (min)',
              data: data.avg_durations,
              borderWidth: 2,
              fill: false,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } }
        }
      });
    })
    .catch(console.error);

  // 2) Contributions (proposed vs validated)
  loadJSON('/dashboard/contrib')
    .then(data => {
      const ctx = document.getElementById('contribPie').getContext('2d');
      new Chart(ctx, {
        type: 'pie',
        data: {
          labels: data.labels,
          datasets: [{
            data: data.counts,
            borderWidth: 1
          }]
        },
        options: { responsive: true }
      });
    })
    .catch(console.error);

  // 3) Répartition par catégorie
  loadJSON('/dashboard/catdist')
    .then(data => {
      const ctx = document.getElementById('catDistBar').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Ressources validées',
            data: data.counts,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } }
        }
      });
    })
    .catch(console.error);
});
