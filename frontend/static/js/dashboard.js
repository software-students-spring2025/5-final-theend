// initialize a Chart.js chart
function initChart(canvasId, type, labels, data, label) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    let datasetOptions = {};
  
    if (canvasId === 'sleepChart') {
      datasetOptions = {
        borderColor: 'blue',
        borderWidth: 2,
        backgroundColor: data.map(v => v >= 7 ? 'rgba(0, 0, 255, 0.2)' : 'rgba(255, 0, 0, 0.2)'),
        pointBackgroundColor: data.map(v => v >= 7 ? 'blue' : 'red')
      };
    } else if (canvasId === 'exerciseChart') {
      datasetOptions = {
        borderColor: 'brown',
        borderWidth: 2,
        backgroundColor: data.map(() => 'rgba(165, 42, 42, 0.2)'),
        pointBackgroundColor: 'brown'
      };
    } else if (canvasId === 'nutritionChart') {
      datasetOptions = {
        backgroundColor: data.map(() => 'rgba(0, 128, 0, 0.2)'),
        borderColor: data.map(() => 'green'),
        borderWidth: 1
      };
    }
  
    new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          ...datasetOptions
        }]
      },
      options: {
        scales: type !== 'pie' ? { y: { beginAtZero: true } } : {}
      }
    });
  }