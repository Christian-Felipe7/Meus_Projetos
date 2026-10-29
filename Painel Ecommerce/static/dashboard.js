let rawOrders = [];
let buckets = {
    ONTIME: [],
    LATE_SEP: [],
    BLOCKED: []
};

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

function resetDashToCurrentMonth() {
    const range = getCurrentMonthRange();
    document.getElementById('dash-start').value = range.start;
    document.getElementById('dash-end').value = range.end;
    sessionStorage.setItem('rymo_start_date', range.start);
    sessionStorage.setItem('rymo_end_date', range.end);
    processDashboard();
}

function onDashDateChange() {
    const s = document.getElementById('dash-start').value;
    const e = document.getElementById('dash-end').value;
    if (s) sessionStorage.setItem('rymo_start_date', s);
    if (e) sessionStorage.setItem('rymo_end_date', e);
    processDashboard();
}

// Extrai apenas a parte DD/MM/YYYY mesmo que venha com horário (ex: "29/10/2026 14:20:10")
function parseBrDate(str) {
    if (!str || str.trim() === '') return null;
    const datePart = str.trim().split(' ')[0];
    const parts = datePart.split('/');
    if (parts.length !== 3) return null;
    return new Date(`${parts[2]}-${parts[1]}-${parts[0]}T00:00:00`);
}

function daysBetween(dateA, dateB) {
    if (!dateA || !dateB) return 0;
    const diffTime = dateB.getTime() - dateA.getTime();
    const days = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return days > 0 ? days : 0;
}

function processDashboard() {
    const startVal = document.getElementById('dash-start').value;
    const endVal = document.getElementById('dash-end').value;

    const startDate = startVal ? new Date(`${startVal}T00:00:00`) : null;
    const endDate = endVal ? new Date(`${endVal}T23:59:59`) : null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    buckets = {
        ONTIME: [],
        LATE_SEP: [],
        BLOCKED: []
    };

    let countF = 0, countL = 0, countSep = 0, countM = 0, countC = 0, countB = 0;

    rawOrders.forEach(order => {
        const emissaoDate = parseBrDate(order.data);
        if (!emissaoDate) return;

        if (startDate && emissaoDate < startDate) return;
        if (endDate && emissaoDate > endDate) return;

        const st = order.status_erp;
        const isSep = order.is_separated;
        const daysOpen = daysBetween(emissaoDate, today);

        // 1. AVALIAÇÃO DE SEPARAÇÃO (DENTRO DO PRAZO vs ATRASADA)
        if (isSep) {
            const sepDate = parseBrDate(order.separated_at) || today;
            const daysToSeparate = daysBetween(emissaoDate, sepDate);
            if (daysToSeparate < 1) {
                buckets.ONTIME.push({ ...order, calc_days: daysToSeparate });
            } else {
                buckets.LATE_SEP.push({ ...order, calc_days: daysToSeparate });
            }
        } else if (st === 'Em Separação' && daysOpen >= 1) {
            // Ainda não foi separado e já tem 1 dia ou mais de espera
            buckets.LATE_SEP.push({ ...order, calc_days: daysOpen });
        }

        // 2. CONTAGEM EXCLUSIVA PARA O GRÁFICO DE SITUAÇÃO ATUAL
        if (st === 'Faturado') {
            countF++;
        } else if (st === 'Em Separação') {
            if (isSep) countSep++;
            else countL++;
        } else if (st === 'Montado') {
            countM++;
        } else if (st === 'Cancelado') {
            countC++;
        } else if (st === 'Bloqueado') {
            countB++;
            buckets.BLOCKED.push({ ...order, calc_days: daysOpen });
        }
    });

    document.getElementById('dash-ok').innerText = buckets.ONTIME.length;
    document.getElementById('dash-delay-sep').innerText = buckets.LATE_SEP.length;
    document.getElementById('dash-blocked').innerText = buckets.BLOCKED.length;

    document.getElementById('dash-chart-total').innerText = `Total analisado: ${countF + countL + countSep + countM + countC + countB} pedidos`;

    updateChart([countF, countL, countSep, countM, countC, countB]);
}

function updateChart(dataCounts) {
    const canvas = document.getElementById('statusChart');
    if (!canvas || typeof Chart === 'undefined') return;
    const ctx = canvas.getContext('2d');

    if (window.statusChartInstance) {
        window.statusChartInstance.destroy();
    }

    window.statusChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Faturados', 'Em Separação', 'Separados', 'Montados', 'Cancelados', 'Bloqueados'],
            datasets: [{
                label: 'Qtd de Pedidos',
                data: dataCounts,
                backgroundColor: [
                    '#22c55e', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444', '#64748b'
                ],
                borderRadius: 6,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#e2e8f0', borderDash: [5, 5] } },
                x: { grid: { display: false } }
            }
        }
    });
}

function openDrilldown(bucketKey) {
    const meta = {
        ONTIME: {
            title: 'Dashboard: Separação Dentro do Prazo',
            subtitle: 'Pedidos cuja separação ocorreu no mesmo dia da emissão (menos de 1 dia).',
            badge: 'SEPARAÇÃO NO PRAZO'
        },
        LATE_SEP: {
            title: 'Dashboard: Separação Atrasada (1 dia ou mais)',
            subtitle: 'Pedidos que levaram 1 dia ou mais para serem separados ou que seguem aguardando separação há 1 dia ou mais.',
            badge: 'ATRASO NA SEPARAÇÃO'
        },
        BLOCKED: {
            title: 'Dashboard: Pedidos Bloqueados',
            subtitle: 'Pedidos Ecommerce atualmente retidos na posição Bloqueado (B).',
            badge: 'BLOQUEIO OPERACIONAL'
        }
    }[bucketKey];

    const list = buckets[bucketKey] || [];
    document.getElementById('dd-title').innerText = meta.title;
    document.getElementById('dd-subtitle').innerText = meta.subtitle;
    document.getElementById('dd-badge').innerText = meta.badge;

    let maxD = 0, sumD = 0;
    list.forEach(item => {
        if (item.calc_days > maxD) maxD = item.calc_days;
        sumD += item.calc_days;
    });
    const avgD = list.length > 0 ? (sumD / list.length).toFixed(1) : 0;

    document.getElementById('dd-kpi-count').innerText = list.length;
    document.getElementById('dd-kpi-max').innerText = `${maxD} dias`;
    document.getElementById('dd-kpi-avg').innerText = `${avgD} dias`;

    const tbody = document.getElementById('dd-tbody');
    tbody.innerHTML = '';

    if (list.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-10 text-dimmed font-bold">
                    <i class="ti ti-mood-smile text-2xl block mb-1"></i>
                    Nenhum pedido enquadrado neste indicador no período selecionado.
                </td>
            </tr>
        `;
    } else {
        list.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-slate-50';
            const sepInfo = item.is_separated
                ? `<span class="text-emerald-700 font-bold">${item.separated_at || 'Separado'} (${item.separator_name || 'S/N'})</span>`
                : `<span class="text-amber-600 font-bold">Aguardando separação</span>`;
            const badgeClass = item.calc_days >= 1 ? 'badge-light-orange' : 'badge-light-green';

            tr.innerHTML = `
                <td class="font-bold text-dimmed">${item.data}</td>
                <td class="text-xs">${sepInfo}</td>
                <td class="font-black text-slate-900">${item.pedido}</td>
                <td class="font-semibold truncate max-w-[240px]" title="${item.cliente}">${item.cliente}</td>
                <td class="text-center"><span class="badge badge-light-blue">${item.status_erp}</span></td>
                <td class="text-center"><span class="badge ${badgeClass}">${item.calc_days} dia(s)</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    const modal = document.getElementById('drilldown-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeDrilldown() {
    const modal = document.getElementById('drilldown-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function initDashboardPage() {
    setInterval(updateClock, 1000);
    updateClock();

    const dataEl = document.getElementById('orders-data');
    if (dataEl) {
        try {
            rawOrders = JSON.parse(dataEl.textContent);
        } catch (e) {
            rawOrders = [];
        }
    }

    const range = getCurrentMonthRange();
    let startVal = sessionStorage.getItem('rymo_start_date');
    let endVal = sessionStorage.getItem('rymo_end_date');

    if (!startVal || startVal.trim() === '') startVal = range.start;
    if (!endVal || endVal.trim() === '') endVal = range.end;

    document.getElementById('dash-start').value = startVal;
    document.getElementById('dash-end').value = endVal;
    sessionStorage.setItem('rymo_start_date', startVal);
    sessionStorage.setItem('rymo_end_date', endVal);

    processDashboard();
}

window.addEventListener('DOMContentLoaded', initDashboardPage);
