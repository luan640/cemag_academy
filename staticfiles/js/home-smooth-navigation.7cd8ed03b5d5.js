/**
 * Otimizações de navegação para a página Home
 * Aplica prefetch e feedback visual em links da home
 */

(function() {
    'use strict';

    const prefetchedLinks = new Set();
    const PREFETCH_DELAY = 50;
    let prefetchTimeout = null;

    /**
     * Prefetch de um link
     */
    function prefetchLink(url) {
        if (prefetchedLinks.has(url)) return;
        
        const linkPrefetch = document.createElement('link');
        linkPrefetch.rel = 'prefetch';
        linkPrefetch.href = url;
        linkPrefetch.as = 'document';
        
        document.head.appendChild(linkPrefetch);
        prefetchedLinks.add(url);
        
        console.log('🚀 Home Prefetch:', url);
    }

    /**
     * Adiciona preconnect
     */
    function addPreconnect() {
        if (document.querySelector('link[rel="preconnect"]')) return;
        
        const preconnect = document.createElement('link');
        preconnect.rel = 'preconnect';
        preconnect.href = window.location.origin;
        document.head.appendChild(preconnect);
    }

    /**
     * Feedback visual ao clicar
     */
    function addClickFeedback(element) {
        if (element.classList.contains('navigating')) return;
        
        element.classList.add('navigating');
        element.style.opacity = '0.7';
        element.style.transform = 'scale(0.98)';
        element.style.transition = 'all 0.15s ease-out';
        
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'navigation-loading';
        loadingIndicator.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Carregando...</span></div>';
        
        if (window.getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }
        
        element.appendChild(loadingIndicator);
    }

    /**
     * Otimiza cards e links da home
     */
    function optimizeHomeLinks() {
        // Trilhas recentes
        const trilhaCards = document.querySelectorAll('.exam-card, .content-panel a, .pending-list a');
        
        trilhaCards.forEach(element => {
            const link = element.href ? element : element.querySelector('a');
            if (!link || !link.href) return;
            
            // Hover
            element.addEventListener('mouseenter', () => {
                clearTimeout(prefetchTimeout);
                prefetchTimeout = setTimeout(() => {
                    prefetchLink(link.href);
                }, PREFETCH_DELAY);
            });
            
            element.addEventListener('mouseleave', () => {
                clearTimeout(prefetchTimeout);
            });
            
            // Touch
            element.addEventListener('touchstart', () => {
                prefetchLink(link.href);
            }, { passive: true });
            
            // Focus
            element.addEventListener('focus', () => {
                prefetchLink(link.href);
            });
            
            // Click feedback
            element.addEventListener('click', function(e) {
                if (this.href || link.href) {
                    addClickFeedback(this);
                }
            });
        });
    }

    /**
     * Otimiza botões de ação
     */
    function optimizeButtons() {
        const buttons = document.querySelectorAll('.btn[href], .btn-link[href]');
        
        buttons.forEach(button => {
            if (!button.href) return;
            
            button.addEventListener('mouseenter', () => {
                clearTimeout(prefetchTimeout);
                prefetchTimeout = setTimeout(() => {
                    prefetchLink(button.href);
                }, PREFETCH_DELAY);
            });
            
            button.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                this.style.transition = 'transform 0.1s ease-out';
            });
        });
    }

    /**
     * Otimiza carregamento do carousel
     */
    function optimizeCarousel() {
        const carousel = document.getElementById('homeCarousel');
        if (!carousel) return;
        
        // Lazy load das imagens do carousel
        const images = carousel.querySelectorAll('img');
        images.forEach((img, index) => {
            if (index > 0) {  // Primeira imagem já carrega
                img.loading = 'lazy';
            }
        });
    }

    /**
     * Progress bar animado
     */
    function animateProgressBar() {
        const progressBar = document.getElementById('home-progress-bar');
        if (!progressBar) return;
        
        const observer = new MutationObserver(() => {
            progressBar.style.transition = 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        observer.observe(progressBar, { attributes: true, attributeFilter: ['style'] });
    }

    /**
     * Otimiza carregamento assíncrono
     */
    function optimizeAsyncLoading() {
        // Observer para detectar conteúdo carregado dinamicamente
        const observer = new MutationObserver(function(mutations) {
            let shouldReinit = false;
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    shouldReinit = true;
                }
            });
            
            if (shouldReinit) {
                setTimeout(() => {
                    optimizeHomeLinks();
                    optimizeButtons();
                }, 100);
            }
        });
        
        // Observa as seções que carregam dinamicamente
        const sections = ['pendencias-trilhas', 'pendencias-avaliacoes'];
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                observer.observe(element, { childList: true, subtree: true });
            }
        });
    }

    /**
     * Prefetch de páginas comuns
     */
    function prefetchCommonPages() {
        setTimeout(() => {
            const commonUrls = [
                '/materiais/pasta/',
                '/biblioteca/',
                // Adicione outras URLs comuns aqui
            ];
            
            commonUrls.forEach(url => {
                if (url !== window.location.pathname) {
                    setTimeout(() => prefetchLink(url), 300);
                }
            });
        }, 2000);
    }

    /**
     * Inicialização
     */
    function init() {
        console.log('✨ Otimizações de navegação da Home inicializadas');
        
        addPreconnect();
        optimizeHomeLinks();
        optimizeButtons();
        optimizeCarousel();
        animateProgressBar();
        optimizeAsyncLoading();
        prefetchCommonPages();
    }

    // Inicializa quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
