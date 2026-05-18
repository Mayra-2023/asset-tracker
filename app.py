<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Verification</title>

    <style>
        body{
            font-family: Arial, sans-serif;
            background:#f4f4f4;
            margin:0;
            padding:0;
        }

        .logo-container{
            text-align:center;
            margin-top:30px;
            margin-bottom:10px;
        }

        .logo{
            height:120px;
        }

        .container{
            max-width:900px;
            margin:auto;
            padding:20px;
            text-align:center;
        }

        h1{
            color:#222;
            margin-bottom:10px;
        }

        p{
            color:#555;
            margin-bottom:40px;
        }

        .cards{
            display:grid;
            grid-template-columns:repeat(auto-fit, minmax(250px,1fr));
            gap:20px;
        }

        .card{
            background:white;
            padding:30px;
            border-radius:12px;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        }

        .card h2{
            margin-bottom:15px;
            color:#333;
        }

        .btn{
            display:inline-block;
            padding:12px 20px;
            background:#007BFF;
            color:white;
            text-decoration:none;
            border-radius:8px;
            margin-top:15px;
        }

        .btn:hover{
            background:#0056b3;
        }

        select{
            padding:10px;
            border-radius:8px;
            border:1px solid #bbb;
            width:100%;
        }
    </style>

</head>
<body>

    <!-- LOGO -->
    <div class="logo-container">
        <img src="{{ url_for('static', filename='logo.png') }}" 
             alt="Logo" 
             class="logo">
    </div>

    <div class="container">

        <h1>Asset Verification</h1>

        <p>Asset registration and verification platform</p>

        <div class="cards">

            <div class="card">
                <h2>Add Asset</h2>
                <p>Register a new asset with photo and details.</p>
                <a href="/add" class="btn">Add Asset</a>
            </div>

            <div class="card">
                <h2>Search Asset</h2>
                <p>Search and verify asset information.</p>
                <a href="/search" class="btn">Search</a>
            </div>

            <div class="card">
                <h2>Update Required</h2>
                <p>View assets that require image updates.</p>
                <a href="/updates" class="btn">View List</a>
            </div>

            <div class="card">
                <h2>Summary</h2>
                <p>Overview of verified and pending assets by depot.</p>
                <a href="/summary" class="btn">View Summary</a>
            </div>

            <!-- EXPORT CSV COM FILTROS -->
            <div class="card">
                <h2>Export Data</h2>
                <p>Download filtered asset data.</p>

                <form action="/export" method="GET" style="display:flex; flex-direction:column; gap:12px;">

                    <label><strong>Select Depot:</strong></label>
                    <select name="depot">
                        <option value="all">All Depots</option>
                        <option value="Maragra">Maragra</option>
                        <option value="Xinavane">Xinavane</option>
                        <option value="Matola">Matola</option>
                        <option value="Mafambisse">Mafambisse</option>
                        <option value="Marromeu">Marromeu</option>
                    </select>

                    <label><strong>Filter:</strong></label>
                    <select name="filter">
                        <option value="all">All Assets</option>
                        <option value="verified">Verified Only</option>
                        <option value="unverified">Unverified Only</option>
                    </select>

                    <button class="btn" type="submit">Download CSV</button>
                </form>
            </div>

        </div>

    </div>

</body>
</html>
