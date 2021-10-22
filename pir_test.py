import asyncio
from asyncio.queues import QueueEmpty
from gpiozero import LED, MotionSensor
from signal import pause

class MotionSensorHandler:
    __when_motion_callback = None

    def __init__(self, pin, when_motion_callback):
        self.__when_motion_callback = when_motion_callback
        self._motion_sensor = MotionSensor(pin)
        self._motion_sensor.when_motion = self.when_motion

    def when_motion(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        future = asyncio.ensure_future(self.__execute_when_motion_callback())
        loop.run_until_complete(future)
        loop.close()

    async def __execute_when_motion_callback(self):
        if self.__when_motion_callback is not None:
            await self.__when_motion_callback()        

class Animate:
    def __init__(self, queue):
        self._queue = queue
        self._loop = asyncio.get_event_loop()
        self._led3 = LED(3, active_high=False)
        self._led4 = LED(4, active_high=False)
        # motion_sensor = MotionSensorHandler(22, self.motion_detected)
        self._pir = MotionSensor(22)
        self._pir.when_motion = self.motion_detected

    async def run(self):        
        print("animation started")
        while True:
            start = await self._queue.get()
            self._led3.on()
            await asyncio.sleep(3)
            self._led3.off()
            self._led4.on()
            await asyncio.sleep(3)
            self._led4.off()

    def motion_detected(self):
        print("motion detected")
        asyncio.run_coroutine_threadsafe(self._queue.put(True), self._loop)


# async def animate(queue):
#     print("animation started")
#     led3 = LED(3)
#     led3.on()
#     led4 = LED(4)
#     led4.on()
#     while True:
#         start = await queue.get()
#         led3.off()
#         await asyncio.sleep(3)
#         led3.on()
#         led4.off()
#         await asyncio.sleep(3)
#         led4.on()


async def main():
    print("starting")
    queue = asyncio.Queue()
    animate = Animate(queue)
    await asyncio.create_task(animate.run())


if __name__ == "__main__":
    asyncio.run(main())    


