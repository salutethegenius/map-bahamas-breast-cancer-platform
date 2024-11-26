document.addEventListener('DOMContentLoaded', function() {
    // Global functions
    window.viewDetails = function(id) {
        fetch(`/registration/${id}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('modalContent').innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('modalContent').innerHTML = 'Error loading details';
            });
    };

    window.exportToCSV = function() {
        window.location.href = "/export_registrations";
    };

    // Dashboard initialization
    const initializeDashboard = function() {
        const searchInput = document.getElementById('searchInput');
        const packageFilter = document.getElementById('packageFilter');
        const table = document.getElementById('registrationsTable');

        if (searchInput && packageFilter && table) {
            searchInput.addEventListener('input', filterTable);
            packageFilter.addEventListener('change', filterTable);

            function filterTable() {
                const searchTerm = searchInput.value.toLowerCase();
                const selectedPackage = packageFilter.value;
                const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

                Array.from(rows).forEach(row => {
                    const companyName = row.cells[0].textContent.toLowerCase();
                    const packageTier = row.cells[1].textContent.toLowerCase();
                    
                    const matchesSearch = companyName.includes(searchTerm);
                    const matchesPackage = !selectedPackage || packageTier.includes(selectedPackage);
                    
                    row.style.display = matchesSearch && matchesPackage ? '' : 'none';
                });
            }
        }
    };

    // Form navigation
    function initializeForm() {
        const sections = document.querySelectorAll('.form-section');
        const progressBar = document.querySelector('.progress-bar');
        const prevBtn = document.getElementById('prev');
        const nextBtn = document.getElementById('next');
        const submitBtn = document.getElementById('submit');
        let currentSection = 0;

        function showSection(sectionIndex) {
            sections.forEach((section, index) => {
                section.classList.remove('active');
                if (index === sectionIndex) section.classList.add('active');
            });

            // Update progress bar
            const progress = ((sectionIndex + 1) / sections.length) * 100;
            if (progressBar) progressBar.style.width = progress + '%';

            // Update buttons
            if (prevBtn) prevBtn.style.display = sectionIndex === 0 ? 'none' : 'block';
            if (nextBtn) nextBtn.style.display = sectionIndex === sections.length - 1 ? 'none' : 'block';
            if (submitBtn) submitBtn.style.display = sectionIndex === sections.length - 1 ? 'block' : 'none';
        }

        if (sections.length > 0) {
            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    if (currentSection > 0) {
                        currentSection--;
                        showSection(currentSection);
                    }
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    if (validateCurrentSection() && currentSection < sections.length - 1) {
                        currentSection++;
                        showSection(currentSection);
                    }
                });
            }

            showSection(0);
        }
    }

    // Form validation
    function validateCurrentSection() {
        const currentForm = document.querySelector('.form-section.active');
        if (!currentForm) return true;

        const fields = currentForm.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        fields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    }

    // Photo preview functionality
    const photoInput = document.querySelector('input[type="file"]');
    const previewDiv = document.getElementById('photoPreview');

    if (photoInput && previewDiv) {
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 16 * 1024 * 1024) {
                    alert('File size exceeds 16MB limit');
                    e.target.value = '';
                    previewDiv.innerHTML = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewDiv.innerHTML = `
                        <img src="${e.target.result}" 
                             alt="Contact photo preview" 
                             style="max-width: 200px; max-height: 200px; border-radius: 4px;">`;
                };
                reader.readAsDataURL(file);
            } else {
                previewDiv.innerHTML = '';
            }
        });
    }

    // Handle form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateCurrentSection()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Initialize form if on registration page
    if (document.querySelector('.form-section')) {
        initializeForm();
    }

    // Initialize dashboard if on dashboard page
    if (document.getElementById('registrationsTable')) {
        initializeDashboard();
    }
});