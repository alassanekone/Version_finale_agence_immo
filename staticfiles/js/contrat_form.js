function handleContractTypeChange(contractType) {
    const dateDebutGroup = document.querySelector('#div_id_date_debut');
    const dateFinGroup = document.querySelector('#div_id_date_fin');
    const dateVenteGroup = document.querySelector('#div_id_date_vente');

    if (contractType === 'vente') {
        // Pour un contrat de vente
        dateDebutGroup.style.display = 'none';
        dateFinGroup.style.display = 'none';
        dateVenteGroup.style.display = 'block';
    } else {
        // Pour un contrat de location
        dateDebutGroup.style.display = 'block';
        dateFinGroup.style.display = 'block';
        dateVenteGroup.style.display = 'none';
    }
}

// Exécuter au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    const contractTypeSelect = document.querySelector('#id_type_contrat');
    if (contractTypeSelect) {
        handleContractTypeChange(contractTypeSelect.value);
    }
});
