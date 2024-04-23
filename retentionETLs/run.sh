if [ -d "$HOME/.local/bin" ] ;
then
    PATH="$HOME/.local/bin:$PATH";
fi
test_conf config set PREFECT_API_URL="http://prefect-server:4200/api"