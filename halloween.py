# 
# The Fabulous Halloween Controller!
#
import signal 
import asyncio
import random
from gpiozero import LED, MotionSensor


class Animation:
    """Base class for an animation decoration
    """
    def __init__(self, gpio_pin):
        self._gpio = LED(gpio_pin, active_high=False)

    async def run(self, duration=0.5):
        self._gpio.on()
        await asyncio.sleep(duration)
        self._gpio.off()        


class Scene:
    """This collects all the animations and controls them to
    create a 'scene'
    """
    def __init__(self, queue):
        self.queue = queue
        self.loop = asyncio.get_event_loop()
        self.projector = Animation(2) # nightmare before christmas projector
        self.scarecrow = Animation(3)
        self.black_ghoul = Animation(4)
        self.white_ghoul = Animation(27)
        self.jack_o_lanterns = Animation(21)
        self.mirror = Animation(13)
        self.anim_7 = Animation(26)
        self.anim_8 = Animation(23)
        self.pir1 = MotionSensor(22)
        self.pir2 = MotionSensor(12)
        self.pir1.when_motion = self.motion_detected
        self.pir2.when_motion = self.motion_detected

        self.animations = [
            self.scarecrow,
            self.black_ghoul,
            self.white_ghoul,
            self.jack_o_lanterns,
            self.mirror,
        ]

    def motion_detected(self):
        asyncio.run_coroutine_threadsafe(self.queue.put(True), self.loop)

    async def run(self):
        while True:
            start = await self.queue.get()
            tasks = [self.projector.run(10)]
            count = random.randint(2,3)
            tasks.extend([
                animation.run(duration=0.5)
                for animation in random.sample(self.animations, count)
            ])
            await asyncio.gather(*tasks)
            # empty the queue so we don't have to many motion activated 
            # scenes running
            while not self.queue.empty():
                self.queue.get_nowait()

async def main():
    scene = Scene(asyncio.Queue())
    await asyncio.create_task(scene.run())


if __name__ == "__main__":
    asyncio.run(main())
