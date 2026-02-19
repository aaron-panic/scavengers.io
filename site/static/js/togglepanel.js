document.addEventListener('DOMContentLoaded', () => {
    const panels = document.querySelectorAll('.wid-panel');

    panels.forEach((panel) => {
        const toggleBtn = panel.querySelector('.wid-panel-toggle');
        if (!toggleBtn) return;

        const collapseFooter = panel.dataset.collapseFooter !== 'false';

        const setCollapsed = (collapsed) => {
            panel.classList.toggle('wid-panel-collapsed', collapsed);
            panel.classList.toggle('wid-panel-expanded', !collapsed);

            if (collapsed && collapseFooter) {
                panel.classList.add('wid-panel-hide-footer');
            } else {
                panel.classList.remove('wid-panel-hide-footer');
            }

            toggleBtn.textContent = collapsed ? '▼' : '▲';
            toggleBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        };

        const startsCollapsed = panel.classList.contains('wid-panel-start-collapsed');
        setCollapsed(startsCollapsed);

        toggleBtn.addEventListener('click', () => {
            const isCollapsed = panel.classList.contains('wid-panel-collapsed');
            setCollapsed(!isCollapsed);
        });
    });
});
