# NATS Messaging System Explained

## Test Setup
In order to test NATS CORE (messaging system) we have install in our local
docker installation a NATS Server running in part 4222 and a NATS-cli instance to
execute commands. To install this setup follow this command

```shell
docker-compose up -d
```

## NATS Context
Before you start interacting with NATS Test ecosystem you need to register
the NATS Connection, otherwise in NATS terminology NATS Context

The commands need to be executed are the following: `nats context add ${name} --server ${server-ip}:${port} --description ${description} --select`

for this particular example, using the nats server installed in the previous step the setup is the following

```shell
nats context add docker --server nats-server:4222 --description "Test NATS Server" --select
```

To retrieve all registered contexts use this command: `nats context ls`

## NATS Publisher
A NATS Publisher sends messages to a subject as follows

```shell
nats pub hello.world "Hi Dude"

nats pub hello.world  "{'msg': 'hello'}"
```

The `count` flag can be used to send multiple instances of the same message and can be used as follows
```shell
nats pub hello.world "Hi Dude" --count 10

nats pub hello.world  "{'msg': 'hello'}" --count 10
```

## NATS Subscriber
### Subscription to a prefixed subject
A subscriber instance needs to be subscribed on a subject with this command
```shell
nats sub hello.world
```

### Subscriber groups
In order to scale the message consumption subscribers can format groups where the server performs load balancing of messages.
We have set the setup below:
+ Subscriber 1 (Terminal 1): `nats sub hello.world --queue panos`
+ Subscriber 2 (Terminal 2): `nats sub hello.world --queue panos`
+ Publisher (Terminal 3): `nats pub hello.world "hey there"`

### Wildcards
A subscriber can listen more than one subjects using wildcards
```shell
nats sub "hello.*" --queue panos
```

The subscriber above will consume messages from the following producers (e.g. where their subject start with hello.)

```shell
nats pub hello.world "hey there"
nats pub hello.jeremy "hey dude"
```