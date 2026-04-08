// Client-side search and filter functionality

document.addEventListener("DOMContentLoaded", function () {
    const header = document.querySelector(".app-header");
    const revealItems = document.querySelectorAll("[data-reveal]");

    if (header) {
        function syncHeaderState() {
            if (window.scrollY > 16) {
                header.classList.add("compact");
            } else {
                header.classList.remove("compact");
            }
        }

        syncHeaderState();
        window.addEventListener("scroll", syncHeaderState, { passive: true });
    }

    if (revealItems.length) {
        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("revealed");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.08 }
        );

        revealItems.forEach(function (item, index) {
            item.style.transitionDelay = Math.min(index * 55, 280) + "ms";
            observer.observe(item);
        });
    }

    document.querySelectorAll(".table").forEach(function (table) {
        table.classList.add("table-modern");
    });

    const searchInput = document.getElementById("search-input");
    const filterCategoria = document.getElementById("filter-categoria");
    const filterSexo = document.getElementById("filter-sexo");
    const tableBody = document.getElementById("table-body");

    if (searchInput && tableBody) {
        function applyFilters() {
            const searchText = searchInput.value.toLowerCase().trim();
            const categoriaValue = filterCategoria ? filterCategoria.value : "";
            const sexoValue = filterSexo ? filterSexo.value : "";
            const rows = tableBody.querySelectorAll("tr");

            rows.forEach(function (row) {
                const nombre = (row.dataset.nombre || "").toLowerCase();
                const apellido = (row.dataset.apellido || "").toLowerCase();
                const dni = (row.dataset.dni || "").toLowerCase();
                const categoria = row.dataset.categoria || "";
                const sexo = row.dataset.sexo || "";

                const matchesSearch =
                    !searchText ||
                    nombre.includes(searchText) ||
                    apellido.includes(searchText) ||
                    dni.includes(searchText);

                const matchesCategoria = !categoriaValue || categoria === categoriaValue;
                const matchesSexo = !sexoValue || sexo === sexoValue;

                row.style.display =
                    matchesSearch && matchesCategoria && matchesSexo ? "" : "none";
            });
        }

        searchInput.addEventListener("input", applyFilters);
        if (filterCategoria) filterCategoria.addEventListener("change", applyFilters);
        if (filterSexo) filterSexo.addEventListener("change", applyFilters);
    }

    const refTableBody = document.getElementById("referencias-table-body");
    const refSearchInput = document.getElementById("ref-search-input");
    const refFilterDeporte = document.getElementById("ref-filter-deporte");
    const refFilterCategoria = document.getElementById("ref-filter-categoria");
    const refFilterSexo = document.getElementById("ref-filter-sexo");

    if (refTableBody) {
        function applyReferenceFilters() {
            const searchText = (refSearchInput ? refSearchInput.value : "").toLowerCase().trim();
            const deporteText = (refFilterDeporte ? refFilterDeporte.value : "").toLowerCase().trim();
            const categoriaText = (refFilterCategoria ? refFilterCategoria.value : "").toLowerCase().trim();
            const sexoValue = refFilterSexo ? refFilterSexo.value : "";

            refTableBody.querySelectorAll("tr").forEach(function (row) {
                const nombre = (row.dataset.nombre || "").toLowerCase();
                const deporte = (row.dataset.deporte || "").toLowerCase();
                const categoria = (row.dataset.categoria || "").toLowerCase();
                const sexo = row.dataset.sexo || "";

                const matchesSearch =
                    !searchText ||
                    nombre.includes(searchText) ||
                    deporte.includes(searchText) ||
                    categoria.includes(searchText);
                const matchesDeporte = !deporteText || deporte.includes(deporteText);
                const matchesCategoria = !categoriaText || categoria.includes(categoriaText);
                const matchesSexo = !sexoValue || sexo === sexoValue;

                row.style.display =
                    matchesSearch && matchesDeporte && matchesCategoria && matchesSexo ? "" : "none";
            });
        }

        if (refSearchInput) refSearchInput.addEventListener("input", applyReferenceFilters);
        if (refFilterDeporte) refFilterDeporte.addEventListener("input", applyReferenceFilters);
        if (refFilterCategoria) refFilterCategoria.addEventListener("input", applyReferenceFilters);
        if (refFilterSexo) refFilterSexo.addEventListener("change", applyReferenceFilters);
    }

    // Bulk selection (checkboxes)
    const selectAll = document.getElementById("select-all");
    const bulkActions = document.getElementById("bulk-actions");
    const countSelected = document.getElementById("count-selected");

    if (selectAll && bulkActions) {
        function updateBulkUI() {
            const checks = document.querySelectorAll(".row-check:checked");
            const total = checks.length;
            if (total > 0) {
                bulkActions.classList.remove("d-none");
                countSelected.textContent = total;
            } else {
                bulkActions.classList.add("d-none");
            }
            // Update select-all state
            const allChecks = document.querySelectorAll(".row-check");
            selectAll.checked = allChecks.length > 0 && total === allChecks.length;
            selectAll.indeterminate = total > 0 && total < allChecks.length;
        }

        selectAll.addEventListener("change", function () {
            document.querySelectorAll(".row-check").forEach(function (cb) {
                cb.checked = selectAll.checked;
            });
            updateBulkUI();
        });

        document.addEventListener("change", function (e) {
            if (e.target.classList.contains("row-check")) {
                updateBulkUI();
            }
        });
    }
});

// Confirm delete dialogs
function confirmarEliminar(nombre, tipo) {
    if (tipo === "jugador") {
        return confirm(
            "¿Seguro que querés eliminar a " + nombre + "? Se eliminarán todas sus antropometrías."
        );
    } else {
        return confirm("¿Seguro que querés eliminar la medición del " + nombre + "?");
    }
}

// Compare selected anthropometries
function compararSeleccionadas() {
    const checks = document.querySelectorAll(".row-check:checked");
    if (checks.length < 2) {
        alert("Seleccioná al menos 2 mediciones para comparar.");
        return;
    }
    const ids = Array.from(checks).map(function (cb) { return cb.value; }).join(",");
    const form = document.getElementById("form-masivo");
    const baseUrl = form ? form.dataset.compararUrl : "/antropometrias/comparar";
    window.location.href = baseUrl + "?ids=" + ids;
}
