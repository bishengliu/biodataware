$('table').DataTable({
    responsive: true,
    "iDisplayLength": 50,
    "order": [[3, "desc"]],
    columnDefs: [
        { targets: 'no-sort', orderable: false }
    ]
});