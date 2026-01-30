// Generic submission confirmation
document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll('.confirm-action');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const message = this.getAttribute('data-message');

            if (!confirm(message))
                event.preventDefault();
        });
    });
});