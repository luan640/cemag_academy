document.addEventListener("DOMContentLoaded", () => {
    fetch('api/trilhas_por_setor')
    .then(response => response.json())
    .then(data => {
        const setores_nomes = Object.keys(data);
        const trilhas_quantidade = Object.values(data);

        // Array de cores para cada barra
        const colors = [
            'rgba(255, 99, 132, 0.2)', // Red
            'rgba(54, 162, 235, 0.2)', // Blue
            'rgba(255, 206, 86, 0.2)', // Yellow
            'rgba(75, 192, 192, 0.2)', // Teal
            'rgba(153, 102, 255, 0.2)', // Purple
            'rgba(255, 159, 64, 0.2)'  // Orange
        ];

        // Cria um array de cores correspondente à quantidade de trilhas
        const backgroundColors = trilhas_quantidade.map((_, index) => colors[index % colors.length]);
        const borderColors = trilhas_quantidade.map((_, index) => colors[index % colors.length].replace('0.2', '1')); // Cores mais escuras para bordas

        const ctx1 = document.getElementById('myChart1');
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: setores_nomes,
                datasets: [{
                    label: 'Quantidade de Trilhas disponíveis por Setor',
                    data: trilhas_quantidade,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1 // Exibe apenas números inteiros
                        }
                    },
                    x: {
                        display: false,
                        ticks: {
                            font: {
                                size: 7, // Diminui o tamanho da fonte dos rótulos do eixo X
                                weight: 'bold' // Deixa a fonte em negrito
                            }
                        }
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching data:', error));

    // Função para buscar os dados da API e renderizar o gráfico
    fetch('api/assiduidade_por_setor')
    .then(response => response.json())
    .then(data => {
        // `data` é um objeto no formato { "TI": "50.00%", "RH": "75.00%", ... }

        // Extrair setores (labels) e proporções (dados) do objeto retornado pela API
        const setores = Object.keys(data);
        const proporcoes = Object.values(data).map(valor => parseFloat(valor.replace('%', '')));

        // Array de cores para cada barra
        const colors = [
            'rgba(255, 99, 132, 0.2)', // Red
            'rgba(54, 162, 235, 0.2)', // Blue
            'rgba(255, 206, 86, 0.2)', // Yellow
            'rgba(75, 192, 192, 0.2)', // Teal
            'rgba(153, 102, 255, 0.2)', // Purple
            'rgba(255, 159, 64, 0.2)'  // Orange
        ];

        const backgroundColors = setores.map((_, index) => colors[index % colors.length]);
        const borderColors = setores.map((_, index) => colors[index % colors.length].replace('0.2', '1')); // Cores mais escuras para bordas

        // Criar o gráfico de barras
        const ctx2 = document.getElementById('myChart2').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: setores, // Nome dos setores
                datasets: [{
                    label: 'Assiduidade por Setor (%)',
                    data: proporcoes, // Porcentagem de visualizações
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Assiduidade (%)'
                        }
                    },
                    x: {
                        display:false,
                        title: {
                            display: true,
                            text: 'Setores'
                        }
                    }
                }
            }
        });
    })
    .catch(error => console.error('Erro ao carregar dados da API:', error));
});