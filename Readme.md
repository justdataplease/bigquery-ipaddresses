# Understanding IP Addresses for Data Analysis - A practical example using BigQuery

Read original article [here](https://medium.com/geekculture/understanding-ip-addresses-for-data-analysis-a-practical-example-using-bigquery-3a6d409e977f).

We will gather a collection of random IP addresses from the internet and treat each one as a unique customer. We will then simulate some fake orders to analyze customer behavior based on their location.

If you want to just test or use this functionality in BigQuery, without implementing it, go to — 8. IP Address geographic distribution Public Demo.

## How to reproduce

***Perform the following actions

1. Create a free account at [MaxMind](https://www.maxmind.com/) and find MaxMind's Licence Key in your profile.
2. Copy and rename .env_sample to .env
3. Update MAXMIND_LICENCE_KEY variable with your own MaxMind's License Key.

***Replace the following with your own

1) \<your-project-id>

### 1. Clone the repository

    git clone https://github.com/justdataplease/bigquery-ipaddresses.git

### 2. Download MaxMind's GeoLite 2 database.

This will download the latest MaxMind's GeoLite 2 City database in zip format.

    pip install -r requirements.txt
    python update_db.py

As a result, a folder named GeoLite2-City-CSV_YYYYMMDD will be created (where YYYYMMDD is the current date).

### 3. Upload GeoLite 2 City database to BigQuery

Next, we need to navigate to the folder named GeoLite2-City-CSV_YYYYMMDD.

      cd .\GeoLite2-City-CSV_YYYYMMDD

The following files will exist inside this folder :

      GeoLite2-City-Blocks-IPv4.csv
      GeoLite2-City-Blocks-IPv6.csv
      GeoLite2-City-Locations-en.csv

We now need to create a new dataset in BigQuery.

      bq mk ip_address

Finally, we should run the following commands to upload the CSV files to the new dataset. 
For this tutorial, we will be using the Europe (eu) location.

      bq load --replace --location=eu --project_id=<your-project-id> --skip_leading_rows=1
      ip_address.geolite2_city_blocks_ipv4 GeoLite2-City-Blocks-IPv4.csv "network:STRING,geoname_id:
      INTEGER,registered_country_geoname_id:INTEGER,represented_country_geoname_id:INTEGER,is_anonymous_proxy:
      BOOL,is_satellite_provider:BOOL,postal_code:STRING,latitude:FLOAT64,longitude:FLOAT64,accuracy_radius:FLOAT64"
      
      bq load --replace --location=eu --project_id=<your-project-id> --skip_leading_rows=1
      ip_address.geolite2_city_blocks_ipv6 GeoLite2-City-Blocks-IPv6.csv "network:STRING,geoname_id:
      INTEGER,registered_country_geoname_id:INTEGER,represented_country_geoname_id:INTEGER,is_anonymous_proxy:
      BOOL,is_satellite_provider:BOOL,postal_code:STRING,latitude:FLOAT64,longitude:FLOAT64,accuracy_radius:FLOAT64"
      
      bq load --replace --location=eu --project_id=<your-project_id> --skip_leading_rows=1
      ip_address.geolite2_city_locations
      GeoLite2-City-Locations-en.csv "geoname_id:INTEGER,locale_code:STRING,continent_code:STRING,continent_name:
      STRING,country_iso_code:STRING,country_name:STRING,subdivision_1_iso_code:STRING,subdivision_1_name:
      STRING,subdivision_2_iso_code:STRING,subdivision_2_name:STRING,city_name:STRING,metro_code:STRING,time_zone:
      STRING,is_in_european_union:BOOL"

### 4. Create new tables

IP Addresses found in MaxMind's Geolite2 Database are in CIDR notation. For us to be able to use them to perform IP Address Lookup we need to split them into the network bin and the network mask.
As an example we can run the following query:

    -- Input
    SELECT '79.166.18.62' ip_address,NET.IP_TO_STRING((NET.IP_FROM_STRING('79.166.18.62') & NET.IP_NET_MASK(4, 16))) network_bin, NET.IP_TO_STRING(NET.IP_NET_MASK(4, 16)) net_mask
    -- Output
    ip_address     network_bin     net_mask
    79.166.18.62   79.166.0.0      255.255.0.0

Finally, to create the new tables we should run the following:

      CREATE OR REPLACE TABLE `<your-project_id>.ip_address.geolite2_city_ipv4`
      AS
      SELECT
      -- Split CIDR notation to the network bin and the netmask.
      NET.IP_FROM_STRING(REGEXP_EXTRACT(network, r'(.*)/' )) network_bin,
      CAST(REGEXP_EXTRACT(network, r'/(.*)' ) AS INT64) mask,
      l.city_name, l.country_iso_code, l.country_name, b.latitude, b.longitude
      FROM `ip_address.geolite2_city_blocks_ipv4` b
      JOIN `ip_address.geolite2_city_locations` l
      USING(geoname_id);

      CREATE OR REPLACE TABLE `<your-project_id>.ip_address.geolite2_city_ipv6`
      AS
      SELECT
      -- Split CIDR notation to the network bin and the netmask.
      NET.IP_FROM_STRING(REGEXP_EXTRACT(network, r'(.*)/' )) network_bin,
      CAST(REGEXP_EXTRACT(network, r'/(.*)' ) AS INT64) mask,
      l.city_name, l.country_iso_code, l.country_name, b.latitude, b.longitude
      FROM `ip_address.geolite2_city_blocks_ipv6` b
      JOIN `ip_address.geolite2_city_locations` l
      USING(geoname_id);

### 5. Create a sample dataset

For educational purposes,  we will use a list of free HTTP proxy addresses as IPv4 Addresses. These addresses are collected daily in [this GitHub](https://github.com/TheSpeedX/PROXY-List) repository.  
In this example, we will only use IPv4 addresses but if you want to also test IPv6 addresses check out section 8. IP Address geographic distribution Public Demo.

We will also assume that these IP Addresses identify customers — an ip_address is a customer_id — and we will generate some fake orders in order to inspect behavioral patterns.

Inside the file collect_free_proxies.py, we can find 2 functions:

The save_ipaddresses() function retrieves and returns a list of HTTP proxy addresses. The create_fake_orders() function generates 100,000 fake orders for the years 2021-2023, with random amounts and timestamps chosen uniformly from a range. To create diverse customer behavior patterns for each order, a customer is randomly selected with a probability from the Beta(2,2) distribution.

We can initiate both functions by running the following:

    cd ..
    python collect_free_proxies.py

As a result, we will get a CSV file called free-proxies.csv and a CSV called fake-orders.csv which we will upload to BigQuery. 

### 6. Upload IP Addresses to BigQuery

To upload free-proxies.csv and fake-orders.csv to BigQuery we should run the following:

      bq load --replace --location=eu --project_id=<your-project-id> --skip_leading_rows=1 ip_address.example_ip_addresses free-proxies.csv "ip_address:STRING"

      bq load --replace --location=eu --project_id=<your-project-id> --skip_leading_rows=1 ip_address.example_orders fake-orders.csv "customer_id:STRING,amount:FLOAT,datetime:DATETIME"

### 7. IP Address geographic distribution

In this step we will retrieve geolocation information (i.e Country and City) for the IP Addresses we have collected in Step 5. We will also materialize the results into a table in order to use it for further analysis.

    CREATE OR REPLACE TABLE ip_address.example_ip_addresses_with_location AS
    WITH sample_dataset AS (
    SELECT ip_address FROM ip_address.example_ip_addresses
    ),
    -- Find IP address version and convert string IP address to binary format (bytes).
    sample_dataset_1 AS (
    SELECT
    ip_address,
    NET.SAFE_IP_FROM_STRING(ip_address) ip_address_in_bytes,
    CASE BYTE_LENGTH(NET.SAFE_IP_FROM_STRING(ip_address))
    WHEN 4 THEN 'IPv4'
    WHEN 16 THEN 'IPv16'
    ELSE 'other' END ip_address_version
    FROM sample_dataset
    ),
    -----PROCESS IPV4 Addresses
    -- Select only IPv4 IP Addresses
    ipv4_addresses AS (
    SELECT DISTINCT * FROM sample_dataset_1 WHERE ip_address_version='IPv4'
    ),
    -- Create all possible netmasks from 255.0.0.0 to 255.255.255.255
    ipv4_netmasks AS (
    SELECT mask FROM UNNEST(GENERATE_ARRAY(8,32)) mask
    ),
    -- Lookup Addresses on MaxMind's Geolite2 Database
    ipv4d_addresses AS (
    SELECT * FROM
    (
    -- Find the network bin that identifies the network
    -- to which ip address belongs
    SELECT ip_address, ip_address_in_bytes & NET.IP_NET_MASK(4, mask) network_bin, mask
    FROM ipv4_addresses
    CROSS JOIN ipv4_netmasks
    )
    -- Keep what matches with MaxMind's Geolite2 Database
    JOIN `eu.geolite2_city_ipv4` USING (network_bin, mask)
    ),
    -----PROCESS IPV6 Addresses
    -- Select only IPv6 IP Addresses
    ipv6_addresses AS (
    SELECT DISTINCT * FROM sample_dataset_1 WHERE ip_address_version='IPv16'
    ),
    -- Create all possible netmasks from ffff:e000:: to ffff:ffff:ffff:ffff::
    ipv6_netmasks AS (
    SELECT mask FROM UNNEST(GENERATE_ARRAY(19,64)) mask
    ),
    -- Lookup Addresses on MaxMind's Geolite2 Database
    ipv6d_addresses AS (
    SELECT * FROM
    (
    -- Find the network bin that identifies the network
    -- to which ip address belongs
    SELECT ip_address, ip_address_in_bytes & NET.IP_NET_MASK(16, mask) network_bin, mask
    FROM ipv6_addresses
    CROSS JOIN ipv6_netmasks
    )
    -- Keep what matches with MaxMind's Geolite2 Database
    JOIN `eu.geolite2_city_ipv6` USING (network_bin, mask)
    )
    -- Combine results
    SELECT * FROM ipv4d_addresses
    UNION ALL
    SELECT * FROM ipv6d_addresses

We will also merge the above table with the table that includes the fake orders that we have generated in Step 5. As we mentioned earlier we assumed that an IP Address (ip_address) refers to a Customer ID (customer_id).

    CREATE OR REPLACE TABLE ip_address.example_orders_with_location AS
    SELECT * FROM eu.example_orders o
    JOIN eu.example_ip_addresses_with_location l ON l.ip_address=o.customer_id

### 8. IP Address geographic distribution Public Demo

We can also test or use the IP Address Lookup functionality in BigQuery without implementing it, by using the publicly
available dataset (eu.geolite2_city_ipv6 , eu.geolite2_city_ipv6). Keep in mind that this dataset will not get updated.
The following example is for Europe-based (eu) data sets.

    WITH sample_dataset AS (
    SELECT ip_address FROM
    UNNEST(['2604:bc80:8001:1064::2','2a02:587:b213:7db4:462e:5d32:93ea:76e8','62.38.6.90','69.162.81.155']) ip_address
    ),
    -- Find IP address version and convert string IP address to binary format (bytes).
    sample_dataset_1 AS (
    SELECT
    ip_address,
    NET.SAFE_IP_FROM_STRING(ip_address) ip_address_in_bytes,
    CASE BYTE_LENGTH(NET.SAFE_IP_FROM_STRING(ip_address))
    WHEN 4 THEN 'IPv4'
    WHEN 16 THEN 'IPv16'
    ELSE 'other' END ip_address_version
    FROM sample_dataset
    ),
    -----PROCESS IPV4 Addresses
    -- Select only IPv4 IP Addresses
    ipv4_addresses AS (
    SELECT DISTINCT * FROM sample_dataset_1 WHERE ip_address_version='IPv4'
    ),
    -- Create all possible netmasks from 255.0.0.0 to 255.255.255.255
    ipv4_netmasks AS (
    SELECT mask FROM UNNEST(GENERATE_ARRAY(8,32)) mask
    ),
    -- Lookup Addresses on MaxMind's Geolite2 Database
    ipv4d_addresses AS (
    SELECT * FROM
    (
    -- Find the network bin that identifies the network
    -- to which ip address belongs
    SELECT ip_address, ip_address_in_bytes & NET.IP_NET_MASK(4, mask) network_bin, mask
    FROM ipv4_addresses
    CROSS JOIN ipv4_netmasks
    )
    -- Keep what matches with MaxMind's Geolite2 Database
    JOIN `eu.geolite2_city_ipv4` USING (network_bin, mask)
    ),
    -----PROCESS IPV6 Addresses
    -- Select only IPv6 IP Addresses
    ipv6_addresses AS (
    SELECT DISTINCT * FROM sample_dataset_1 WHERE ip_address_version='IPv16'
    ),
    -- Create all possible netmasks from ffff:e000:: to ffff:ffff:ffff:ffff::
    ipv6_netmasks AS (
    SELECT mask FROM UNNEST(GENERATE_ARRAY(19,64)) mask
    ),
    -- Lookup Addresses on MaxMind's Geolite2 Database
    ipv6d_addresses AS (
    SELECT * FROM
    (
    -- Find the network bin that identifies the network
    -- to which ip address belongs
    SELECT ip_address, ip_address_in_bytes & NET.IP_NET_MASK(16, mask) network_bin, mask
    FROM ipv6_addresses
    CROSS JOIN ipv6_netmasks
    )
    -- Keep what matches with MaxMind's Geolite2 Database
    JOIN `eu.geolite2_city_ipv6` USING (network_bin, mask)
    )
    -- Combine results
    SELECT * FROM ipv4d_addresses
    UNION ALL
    SELECT * FROM ipv6d_addresses

We can also directly use the final table we have created in Step 7 for analysis:

    SELECT * FROM `justfunctions.eu.example_orders_with_location`