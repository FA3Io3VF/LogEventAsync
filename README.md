# LogEventAsync
An Example for log event and errors in a async web api

# Come funziona

Eventi e errori sono salvati sulla stessa tabella con un flag Event che distingue tra errori e eventi,
la struttura della tabella è la seguente:

```python
class LogError(Base):
    __tablename__ = 'log_error'
    id = Column(Integer, primary_key=True, autoincrement=True)
    error = Column(String, nullable=False)
    function = Column(String, nullable=False)
    motivation = Column(String, nullable=False)
    user = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    event = Column(Boolean, nullable=False, default=False)
```

Per registrare un evento basta chiamare: 

```python
await log_error_actor.register_error(str(e), "startup_event", "Testing", "admin", True)
```

Per ottenere gli errori o gli eventi di un utente:

```python
await log_error_actor.get_user_errors(user, event)
```        
Per ottenere tutti i log in una certa data:

```python
await log_error_actor.get_date_errors(date)
```

Per ottenere tutti i log in un certo intervallo di date:

```python
await log_error_actor.get_date_range_errors(start_date, end_date)
```


Si decide di usare un DB diverso dal resto dell'aplicazione per ridurre il carico dei thread 
sul db principale, il tipo di DB e il modo di connettersi a esso dovrà cambiare in base alle necessità.

# La classe usa l'approccio a attori

L'approccio ad attori è un paradigma di programmazione concorrente e distribuita che
si basa sulla creazione di entità indipendenti, chiamate "attori", 
che interagiscono tra loro solo tramite l'invio di messaggi asincroni.

Ogni attore possiede un proprio stato interno e può eseguire operazioni 
solo su di esso. Inoltre, gli attori non condividono alcuna memoria 
o stato globale e non possono accedere direttamente ai dati degli altri attori. 
Ciò garantisce che gli attori siano isolati l'uno dall'altro e che le 
interazioni tra di loro siano gestite in modo controllato.

L'approccio ad attori è particolarmente utile per la creazione di sistemi 
distribuiti altamente scalabili e resilienti, in quanto consente di gestire 
facilmente la concorrenza e di isolare le parti del sistema che 
possono fallire o avere problemi, minimizzando l'impatto sull'intero sistema.

Inoltre, l'approccio ad attori può semplificare la gestione della concorrenza 
rispetto ad altri approcci, come l'utilizzo di thread o processi, poiché gli 
attori possono essere eseguiti su un singolo thread e gestiti da un sistema 
di attori dedicato che si occupa della gestione della concorrenza e della 
distribuzione degli attori su più nodi di calcolo.

