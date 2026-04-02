// Client-side search and filter functionality

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const filterCategoria = document.getElementById("filter-categoria");
    const filterSexo = document.getElementById("filter-sexo");
    const tableBody = document.getElementById("table-body");

    if (!searchInput || !tableBody) return;

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
