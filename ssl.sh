SSLDIR=data/ssl
CERTDIR=$SSLDIR/certs
KEYDIR=$SSLDIR/keys
COMBINEDDIR=$SSLDIR/combined

rm -rf "$SSLDIR"

mkdir -p "$CERTDIR"
mkdir -p "$KEYDIR"
mkdir -p "$COMBINEDDIR"

openssl req -x509 \
  -sha256 \
  -days 3650 \
  -nodes \
  -newkey rsa:4096 \
  -subj "/C=RU/L=Moscow" \
  -keyout "$KEYDIR/rootCA.key" \
  -out "$CERTDIR/rootCA.crt" 

for domain in starrails.com hoyoverse.com mihoyo.com bhsr.com; do
  openssl req -x509 \
    -newkey rsa:4096 \
    -keyout "$KEYDIR/${domain}.pem" \
    -out "$CERTDIR/${domain}.pem" \
    -CAkey "$KEYDIR/rootCA.key" \
    -CA "$CERTDIR/rootCA.crt" \
    -sha256 \
    -days 3650 \
    -nodes \
    -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=$domain"

  cat "$KEYDIR/${domain}.pem" "$CERTDIR/${domain}.pem" > "$COMBINEDDIR/${domain}.pem"
done

cat "$COMBINEDDIR"/*.pem > "$SSLDIR/keystore.pem"

openssl pkcs12 -export -in "$SSLDIR/keystore.pem" -out "$SSLDIR/keystore.p12" -passout pass:lunar
