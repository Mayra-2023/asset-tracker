html
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Asset Analytics Dashboard</title>

    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
    >

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>


<body class="bg-light">


<div class="container-fluid p-4">


    <!-- =========================
         TITLE
    ========================== -->

    <h2 class="mb-4">
        Asset Analytics Dashboard
    </h2>


    <!-- =========================
         KPI CARDS
    ========================== -->

    <div class="row mb-4">

        <div class="col-md-2">
            <div class="card shadow-sm border-primary">
                <div class="card-body text-center">
                    <h6>Total Assets</h6>
                    <h3>{{ total_assets }}</h3>
                </div>
            </div>
        </div>


        <div class="col-md-2">
            <div class="card shadow-sm border-success">
                <div class="card-body text-center">
                    <h6>Active</h6>
                    <h3>{{ active_assets }}</h3>
                </div>
            </div>
        </div>


        <div class="col-md-2">
            <div class="card shadow-sm border-warning">
                <div class="card-body text-center">
                    <h6>Maintenance</h6>
                    <h3>{{ maintenance_assets }}</h3>
                </div>
            </div>
        </div>


        <div class="col-md-2">
            <div class="card shadow-sm border-danger">
                <div class="card-body text-center">
                    <h6>Missing</h6>
                    <h3>{{ missing_assets }}</h3>
                </div>
            </div>
        </div>


        <div class="col-md-2">
            <div class="card shadow-sm border-dark">
                <div class="card-body text-center">
                    <h6>To Be Scrapped</h6>
                    <h3>{{ to_be_scrapped_assets }}</h3>
                </div>
            </div>
        </div>


        <div class="col-md-2">
            <div class="card shadow-sm border-secondary">
                <div class="card-body text-center">
                    <h6>Scrapped</h6>
                    <h3>{{ scrapped_assets }}</h3>
                </div>
            </div>
        </div>

    </div>


    <!-- =========================
         DEPOT FILTER
    ========================== -->

    <div class="row mb-4">

        <div class="col-md-4">

            <form method="GET">

                <label class="form-label">
                    Select Depot
                </label>

                <select
                    name="depot"
                    class="form-select"
                >

                    <option value="">
                        All Depots
                    </option>


                    {% for depot in depots %}

                    <option
                        value="{{ depot }}"
                        {% if depot == selected_depot %}
                        selected
                        {% endif %}
                    >
                        {{ depot }}
                    </option>

                    {% endfor %}

                </select>


                <button
                    type="submit"
                    class="btn btn-primary mt-2"
                >
                    Filter
                </button>

            </form>

        </div>

    </div>


    <!-- =========================
         CHARTS
    ========================== -->

    <div class="row">


        <!-- DEPOT CHART -->

        <div class="col-md-6">

            <div class="card shadow-sm">

                <div class="card-header">
                    Assets by Depot
                </div>

                <div class="card-body">

                    <canvas id="depotChart"></canvas>

                </div>

            </div>

        </div>


        <!-- STATUS CHART -->

        <div class="col-md-6">

            <div class="card shadow-sm">

                <div class="card-header">

                    {% if selected_depot %}

                        {{ selected_depot }} - Assets by Status

                    {% else %}

                        Assets by Status

                    {% endif %}

                </div>


                <div class="card-body">

                    <canvas id="statusChart"></canvas>

                </div>

            </div>

        </div>

    </div>


    <!-- =========================
         RECENT ASSETS
    ========================== -->

    <div class="card shadow-sm mt-4">

        <div class="card-header">
            Recent Assets
        </div>


        <div class="card-body">

            {% if recent_assets %}

            <div class="table-responsive">

                <table class="table table-striped table-hover">

                    <thead>

                        <tr>

                            <th>Asset ID</th>

                            <th>Depot</th>

                            <th>Status</th>

                            <th>Captured By</th>

                            <th>Capture Date</th>

                        </tr>

                    </thead>


                    <tbody>

                        {% for asset in recent_assets %}

                        <tr>

                            <td>
                                {{ asset[0] }}
                            </td>

                            <td>
                                {{ asset[1] }}
                            </td>

                            <td>
                                {{ asset[2] }}
                            </td>

                            <td>
                                {{ asset[3] }}
                            </td>

                            <td>
                                {{ asset[4] }}
                            </td>

                        </tr>

                        {% endfor %}

                    </tbody>

                </table>

            </div>

            {% else %}

                <p class="text-muted mb-0">
                    No assets found.
                </p>

            {% endif %}

        </div>

    </div>


</div>


<!-- =========================
     CHART JAVASCRIPT
========================== -->

<script>


/* =========================
   DEPOT CHART
========================= */

const depotLabels = {{ depot_labels | tojson }};

const depotValues = {{ depot_values | tojson }};


const depotCanvas =
    document.getElementById('depotChart');


if (depotCanvas) {

    new Chart(
        depotCanvas,
        {
            type: 'bar',

            data: {

                labels: depotLabels,

                datasets: [{

                    label: 'Assets',

                    data: depotValues,

                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#dc3545',
                        '#ffc107',
                        '#6f42c1',
                        '#20c997',
                        '#fd7e14',
                        '#6c757d'
                    ],

                    borderWidth: 1

                }]

            },


            options: {

                responsive: true,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }

                    }

                }

            }

        }
    );

}


/* =========================
   STATUS CHART
========================= */

const statusLabels = {{ status_labels | tojson }};

const statusValues = {{ status_values | tojson }};


const statusCanvas =
    document.getElementById('statusChart');


if (statusCanvas) {

    new Chart(
        statusCanvas,
        {
            type: 'pie',

            data: {

                labels: statusLabels,

                datasets: [{

                    data: statusValues,

                    backgroundColor: [
                        '#198754',
                        '#ffc107',
                        '#dc3545',
                        '#0d6efd',
                        '#6f42c1',
                        '#6c757d',
                        '#20c997',
                        '#fd7e14'
                    ]

                }]

            },


            options: {

                responsive: true,

                plugins: {

                    legend: {
                        position: 'bottom'
                    }

                }

            }

        }
    );

}


</script>


<!-- =========================
     BACK TO HOME
========================== -->

<div style="text-align:center; margin:30px 0;">

    <a
        href="/"
        style="
            display:inline-block;
            padding:12px 24px;
            background:#007BFF;
            color:white;
            text-decoration:none;
            border-radius:8px;
            font-size:16px;
        "
    >
        ← Back to Home
    </a>

</div>


</body>

</html>
```
