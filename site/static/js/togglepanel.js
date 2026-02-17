document.addEventListener('DOMContentLoaded', () => {
    const panels = document.querySelectorAll('.wid-panel');

    panels.forEach(panel => {
        const toggleBtn = panel.querySelector('.wid-panel-toggle');
        const body = panel.querySelector('.wid-panel-body');
        const footer = panel.querySelector('.wid-panel-footer');

        if (!toggleBtn || !body) return;

        if (panel.classList.contains('wid-panel-start-collapsed')) {
            body.style.display = 'none';
            if (footer) footer.style.display = 'none';
        } else {
            body.style.display = ''; 
            if (footer) footer.style.display = '';
        }

        toggleBtn.addEventListener('click', () => {
            const isHidden = (body.style.display === 'none');

            if (isHidden) {
                // expand
                body.style.display = '';
                if (footer) footer.style.display = '';
                toggleBtn.textContent = '▲'; 
            } else {
                // collapse
                body.style.display = 'none';
                if (footer) footer.style.display = 'none';
                toggleBtn.textContent = '▼';
            }
        });
    });
});