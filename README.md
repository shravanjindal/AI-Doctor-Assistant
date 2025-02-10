## AI-Doctor-Assistant

### To run this bot in your local system :

1) `You must have mongo database installed in your system`
<br />

`To start the mongo database (for linux)` : 

```
sudo systemctl start mongod
```

2) `Starting the server`

<br />

`You should be using python==3.12`
<br />

If using conda env : 
```
$ conda create -n <env_name> python=3.12
```

```
$ cd backend
$ pip install -r requirements.txt
```

```
$ uvicorn main:app
```
<br/>

3) `starting the frontend`

```
$ cd frontend
$ npm install
```

```
$ npm run dev
```
<hr />