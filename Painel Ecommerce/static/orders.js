function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { hour12: false });
    const [hours, minutes, seconds] = timeString.split(':');
    const clockEl = document.getElementById('clock-time');
    if (clockEl) {
        clockEl.innerHTML = `${hours}:${minutes}<span class="clock-seconds">${seconds}</span>`;
    }
    const dateEl = document.getElementById('clock-date');
    if (dateEl) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: '2-digit' };
        let dateString = now.toLocaleDateString('pt-BR', options);
        dateEl.innerText = dateString.replace(/\b\w/g, l => l.toUpperCase());
    }
}

let currentKpiFilter = 'INITIAL';

function getCurrentMonthRange() {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const formatToInput = (d) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${dd}`;
    };
    return { start: formatToInput(firstDay), end: formatToInput(today) };
}

function resetToCurrentMonth() {
    const range = getCurrentMonthRange();
    document.getElementById('filter-start').value = range.start;
    document.getElementById('filter-end').value = range.end;
    sessionStorage.setItem('rymo_start_date', range.start);
    sessionStorage.setItem('rymo_end_date', range.end);
    applyFilters();
}

function onDateChange() {
    const s = document.getElementById('filter-start').value;
    const e = document.getElementById('filter-end').value;
    if (s) sessionStorage.setItem('rymo_start_date', s);
    if (e) sessionStorage.setItem('rymo_end_date', e);
    applyFilters();
}

function parseBrazilianDate(dateStr) {
    if (!dateStr) return null;
    const parts = dateStr.split('/');
    return new Date(`${parts[2]}-${parts[1]}-${parts[0]}T00:00:00`);
}

function handleCheckboxClick(event, checkboxEl, isSeparated) {
    event.preventDefault();
    if (!isSeparated) {
        const nome = prompt('OBRIGATÓRIO: Digite o NOME de quem separou o material:');
        if (!nome || nome.trim() === '') {
            alert('Ação bloqueada. O nome do separador é obrigatório.');
            return false;
        }
        checkboxEl.closest('tr').querySelector('input[name=separator_name]').value = nome.trim();
    }
    htmx.trigger(checkboxEl, 'process-toggle');
}

function applyFilters() {
    const searchVal = document.getElementById('filter-search').value.toLowerCase();
    const startVal = document.getElementById('filter-start').value;
    const endVal = document.getElementById('filter-end').value;
    const statusVal = document.getElementById('filter-status').value;

    const startDate = startVal ? new Date(`${startVal}T00:00:00`) : null;
    const endDate = endVal ? new Date(`${endVal}T23:59:59`) : null;

    const rows = document.querySelectorAll('#orders-tbody tr');
    let L = 0, F = 0, M = 0, C = 0, B = 0, separados = 0, total = 0;
    let visibleCount = 0;

    rows.forEach(row => {
        const statusErp = row.getAttribute('data-status-erp');
        const isSeparated = row.getAttribute('data-separated') === 'true';
        const rowCliente = row.getAttribute('data-cliente');
        const rowPedido = row.getAttribute('data-pedido');
        const rowData = row.getAttribute('data-datarow');

        let siglaErp = 'P';
        if (statusErp === 'Em Separação') siglaErp = 'L';
        if (statusErp === 'Faturado') siglaErp = 'F';
        if (statusErp === 'Montado') siglaErp = 'M';
        if (statusErp === 'Cancelado') siglaErp = 'C';
        if (statusErp === 'Bloqueado') siglaErp = 'B';

        let matchesBaseFilters = true;

        if (searchVal && !rowCliente.includes(searchVal) && !rowPedido.includes(searchVal)) {
            matchesBaseFilters = false;
        }

        if (startDate || endDate) {
            const rDate = parseBrazilianDate(rowData);
            if (rDate) {
                if (startDate && rDate < startDate) matchesBaseFilters = false;
                if (endDate && rDate > endDate) matchesBaseFilters = false;
            }
        }

        if (matchesBaseFilters) {
            total++;
            let visualStatus = 'OUTROS';

            if (siglaErp === 'F') { F++; visualStatus = 'F'; }
            else if (siglaErp === 'C') { C++; visualStatus = 'C'; }
            else if (siglaErp === 'B') { B++; visualStatus = 'B'; }
            else if (siglaErp === 'M') { M++; visualStatus = 'M'; }
            else if (siglaErp === 'L') {
                if (isSeparated) { separados++; visualStatus = 'SEP'; }
                else { L++; visualStatus = 'L'; }
            }
            row.setAttribute('data-visual-status', visualStatus);
        }

        let showInTable = matchesBaseFilters;

        if (showInTable) {
            const vStatus = row.getAttribute('data-visual-status');
            if (currentKpiFilter === 'INITIAL') {
                if (vStatus === 'F' || vStatus === 'C') showInTable = false;
            } else if (currentKpiFilter !== 'ALL') {
                if (vStatus !== currentKpiFilter) showInTable = false;
            }
            if (statusVal && siglaErp !== statusVal) showInTable = false;
        }

        row.style.display = showInTable ? '' : 'none';
        if (showInTable) visibleCount++;
    });

    document.getElementById('kpi-total').innerText = total;
    document.getElementById('kpi-l').innerText = L;
    document.getElementById('kpi-f').innerText = F;
    document.getElementById('kpi-m').innerText = M;
    document.getElementById('kpi-c').innerText = C;
    document.getElementById('kpi-b').innerText = B;
    document.getElementById('kpi-sep').innerText = separados;
    document.getElementById('visible-count').innerText = `${visibleCount} pedidos listados nesta visualização`;
}

function handleKpiClick(filterType) {
    currentKpiFilter = filterType;
    sessionStorage.setItem('rymo_kpi_filter', filterType);
    document.querySelectorAll('.kpi-filter').forEach(card => card.classList.remove('ring-4', 'ring-blue-500', 'bg-blue-50/40'));

    if (filterType !== 'INITIAL') {
        const activeCard = document.getElementById('card-' + filterType);
        if (activeCard) activeCard.classList.add('ring-4', 'ring-blue-500', 'bg-blue-50/40');
    }
    applyFilters();
}

function initOrdersPage() {
    setInterval(updateClock, 1000);
    updateClock();

    const range = getCurrentMonthRange();
    let startVal = sessionStorage.getItem('rymo_start_date');
    let endVal = sessionStorage.getItem('rymo_end_date');
    let storedFilter = sessionStorage.getItem('rymo_kpi_filter') || 'INITIAL';

    if (!startVal || startVal.trim() === '') startVal = range.start;
    if (!endVal || endVal.trim() === '') endVal = range.end;

    document.getElementById('filter-start').value = startVal;
    document.getElementById('filter-end').value = endVal;
    sessionStorage.setItem('rymo_start_date', startVal);
    sessionStorage.setItem('rymo_end_date', endVal);

    handleKpiClick(storedFilter);
}

window.addEventListener('DOMContentLoaded', initOrdersPage);

document.body.addEventListener('htmx:afterSettle', function(evt) {
    if (evt.detail.target.tagName === 'TR' || evt.detail.target.id === 'orders-tbody') {
        applyFilters();
    }
});
