if [ -d "$HOME/.local/bin" ] ;
then
    PATH="$HOME/.local/bin:$PATH";
fi
prefect config set PREFECT_API_URL="http://prefect-server:4200/api"

python workpool.py
python block.py