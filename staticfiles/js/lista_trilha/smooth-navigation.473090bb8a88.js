/**
 * Sistema de navegação fluida - Otimizações de performance e UX
 * 
 * Funcionalidades:
 * - Prefetch de links ao passar o mouse (preload instantâneo)
 * - Transições suaves e feedback visual imediato
 * - Loading states otimizados
 * - Cache inteligente de recursos
 */

(function() {
    'use strict';

    // Cache de links já carregados para evitar prefetch duplicado
    const prefetchedLinks = new Set();
    
    // Tempo de delay antes do prefetch (em ms)
    const PREFETCH_DELAY = 50; // Reduzido para 50ms para ser mais agressivo
    
    // Timeout para hover
    let prefetchTimeout = null;
    
    // Flag para saber se o usuário já interagiu
    let userHasInteracted = false;

    /**
     * Cria um link prefetch dinamicamente
     */
    function prefetchLink(url) {
        if (prefetchedLinks.has(url)) return;
        
        // Prefetch do documento
        const linkPrefetch = document.createElement('link');
        linkPrefetch.rel = 'prefetch';
        linkPrefetch.href = url;
        linkPrefetch.as = 'document';
        
        document.head.appendChild(linkPrefetch);
        prefetchedLinks.add(url);
        
        console.log('🚀 Prefetch:', url);
    }

    /**
     * Preconnect para o domínio
     */
    function addPreconnect() {
        if (document.querySelector('link[rel="preconnect"]')) return;
        
        const preconnect = document.createElement('link');
        preconnect.rel = 'preconnect';
        preconnect.href = window.location.origin;
        document.head.appendChild(preconnect);
        
        // DNS-Prefetch como fallback
        const dnsPrefetch = document.createElement('link');
        dnsPrefetch.rel = 'dns-prefetch';
        dnsPrefetch.href = window.location.origin;
        document.head.appendChild(dnsPrefetch);
    }

    /**
     * Adiciona feedback visual instantâneo ao clicar
     */
    function addClickFeedback(element) {
        // Previne múltiplos cliques
        if (element.classList.contains('navigating')) return;
        
        element.classList.add('navigating');
        
        // Mostra indicador de loading
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'navigation-loading';
        loadingIndicator.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Carregando...</span></div>';
        
        // Garante que o elemento tem position relative
        const originalPosition = window.getComputedStyle(element).position;
        if (originalPosition === 'static') {
            element.style.position = 'relative';
        }
        
        element.appendChild(loadingIndicator);
    }

    /**
     * Prefetch inteligente baseado em viewport
     */
    function prefetchVisibleLinks() {
        if (!('IntersectionObserver' in window)) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && userHasInteracted) {
                    const link = entry.target.querySelector('a');
                    if (link && link.href) {
                        // Delay pequeno para não sobrecarregar
                        setTimeout(() => prefetchLink(link.href), 1000);
                    }
                }
            });
        }, {
            rootMargin: '50px' // Começa a carregar 50px antes de entrar na tela
        });
        
        document.querySelectorAll('.exam-card').forEach(card => {
            observer.observe(card);
        });
    }

    /**
     * Inicializa o sistema de prefetch em links de trilhas
     */
    function initPrefetch() {
        // Seleciona todos os links relevantes (trilhas e botões)
        const trilhaLinks = document.querySelectorAll('.trilha-nome, .exam-card-footer a, .exam-card');
        
        trilhaLinks.forEach(element => {
            let link = element;
            
            // Se for um card, pega o link dentro dele
            if (element.classList.contains('exam-card')) {
                link = element.querySelector('a.trilha-nome') || element.querySelector('.exam-card-footer a');
            }
            
            if (!link || !link.href) return;
            
            // Evento: Mouse entra (hover)
            element.addEventListener('mouseenter', () => {
                userHasInteracted = true;
                clearTimeout(prefetchTimeout);
                prefetchTimeout = setTimeout(() => {
                    prefetchLink(link.href);
                }, PREFETCH_DELAY);
            });
            
            // Evento: Mouse sai
            element.addEventListener('mouseleave', () => {
                clearTimeout(prefetchTimeout);
            });
            
            // Evento: Toque em dispositivos móveis
            element.addEventListener('touchstart', () => {
                userHasInteracted = true;
                prefetchLink(link.href);
            }, { passive: true });
            
            // Evento: Focus (acessibilidade)
            element.addEventListener('focus', () => {
                userHasInteracted = true;
                prefetchLink(link.href);
            });
        });
    }

    /**
     * Adiciona feedback visual nos botões e cards
     */
    function initClickFeedback() {
        // Cards clicáveis
        document.querySelectorAll('.exam-card').forEach(card => {
            card.addEventListener('click', function(e) {
                // Ignora cliques em botões específicos dentro do card
                if (e.target.closest('.btn-outline-secondary:not(.btn-ambiente-prova), [onclick*="openInscritosModal"]')) {
                    return;
                }
                
                // Ignora se já está navegando
                if (this.classList.contains('navigating')) {
                    e.preventDefault();
                    return;
                }
                
                const mainLink = this.querySelector('.trilha-nome') || this.querySelector('.exam-card-footer a');
                if (mainLink && !e.defaultPrevented) {
                    e.preventDefault();
                    addClickFeedback(this);
                    
                    // Navega após o feedback visual (reduzido para 100ms)
                    setTimeout(() => {
                        window.location.href = mainLink.href;
                    }, 100);
                }
            });
            
            // Remove o cursor pointer se não tiver link
            const hasLink = card.querySelector('a');
            if (!hasLink) {
                card.style.cursor = 'default';
            }
        });
        
        // Botões diretos
        document.querySelectorAll('.exam-card-footer a, .trilha-nome').forEach(button => {
            button.addEventListener('click', function(e) {
                const card = this.closest('.exam-card');
                if (card && !card.classList.contains('navigating')) {
                    addClickFeedback(card);
                }
            });
        });
    }

    /**
     * Otimiza lazy loading de imagens
     */
    function optimizeImages() {
        if ('loading' in HTMLImageElement.prototype) {
            const images = document.querySelectorAll('img[loading="lazy"]');
            images.forEach(img => {
                img.addEventListener('load', function() {
                    this.classList.add('loaded');
                });
            });
        }
    }

    /**
     * Adiciona service worker para cache offline (se disponível)
     */
    function initServiceWorker() {
        if ('serviceWorker' in navigator && !navigator.serviceWorker.controller) {
            // Apenas registra se ainda não houver um service worker
            // Não implementamos o SW aqui, mas preparamos o terreno
            console.log('🔧 Service Worker suportado');
        }
    }

    /**
     * Prefetch de recursos estáticos comuns
     */
    function prefetchCommonResources() {
        // Lista de páginas/recursos comuns que provavelmente serão acessados
        const commonPages = [
            '/materiais/pasta/',
            // Adicione outras URLs comuns aqui
        ];
        
        // Só faz prefetch depois que o usuário interage
        if (userHasInteracted) {
            commonPages.forEach(page => {
                if (page !== window.location.pathname) {
                    setTimeout(() => prefetchLink(page), 2000);
                }
            });
        }
    }

    /**
     * Monitora inatividade para fazer prefetch proativo
     */
    function initIdlePrefetch() {
        let idleTimer;
        
        const resetIdleTimer = () => {
            clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                // Após 2s de inatividade, prefetch dos links visíveis
                prefetchVisibleLinks();
                prefetchCommonResources();
            }, 2000);
        };
        
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetIdleTimer, { passive: true });
        });
        
        resetIdleTimer();
    }

    /**
     * Inicialização quando DOM estiver pronto
     */
    function init() {
        console.log('✨ Sistema de navegação fluida inicializado');
        
        addPreconnect();
        initPrefetch();
        initClickFeedback();
        optimizeImages();
        initServiceWorker();
        
        // Inicia monitoramento de inatividade após 1s
        setTimeout(initIdlePrefetch, 1000);
        
        // Re-inicializa após carregamento dinâmico (paginação, filtros)
        const observer = new MutationObserver(function(mutations) {
            let shouldReinit = false;
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    shouldReinit = true;
                }
            });
            
            if (shouldReinit) {
                // Debounce para evitar múltiplas reinicializações
                setTimeout(() => {
                    initPrefetch();
                    initClickFeedback();
                }, 100);
            }
        });
        
        const examsGrid = document.querySelector('.exams-grid');
        if (examsGrid) {
            observer.observe(examsGrid, { childList: true, subtree: true });
        }
    }

    // Inicializa quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
