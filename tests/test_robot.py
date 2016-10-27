from panopticon import Robot

if __name__ == '__main__':
    # Application will initialize robots (eventually, should pull robots from DB)
    bpl = Robot()
    # Initialize 'update workers'
    updater = ClientWorker(bpl)
    bpl.client.status('TipDressCounter')
    bpl.client.subscribe('TipDressCounter', None)
    # Start update workers
    updater.start()

    while True:
        time.sleep(10)
        print("Alive")