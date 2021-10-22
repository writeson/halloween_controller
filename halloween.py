# 
# The Fabulous Halloween Controller!
#
import signal 
import asyncio
import random
from gpiozero import LED, MotionSensor


class Scene:
    """This collects all the animations and controls them to
    create a 'scene'
    """
    def __init__(self, queue):
        self.queue = queue
        self.loop = asyncio.get_event_loop()
        self.projector = LED(2, active_high=False) # nightmare before christmas projector
        self.scarecrow = LED(3, active_high=False)
        self.black_ghoul = LED(4, active_high=False)
        self.white_ghoul = LED(27, active_high=False)
        self.jack_o_lanterns = LED(21, active_high=False)
        self.mirror = LED(13, active_high=False)
        self.anim_7 = LED(26, active_high=False)
        self.anim_8 = LED(23, active_high=False)
        self.pir1 = MotionSensor(22)
        # self.pir2 = MotionSensor(12)
        # self.pir1.when_motion = self.motion_detected
        # self.pir2.when_motion = self.motion_detected

        self.animations = [
            self.scarecrow,
            self.black_ghoul,
            self.white_ghoul,
            self.jack_o_lanterns,
            self.mirror,
        ]

    def motion_detected(self):
        asyncio.run_coroutine_threadsafe(self.queue.put(True), self.loop)

    async def run_animation(self, animation: LED, duration: float):
        animation.on()
        await asyncio.sleep(duration)
        animation.off()

    async def run(self):
        while True:
            start = await self.queue.get()
            tasks = [self.run_animation(self.projector, 1.0)]
            count = random.randint(2,3)
            tasks.extend([
                self.run_animation(animation, duration=0.5)
                for animation in random.sample(self.animations, count)
            ])
            await asyncio.gather(*tasks)
            # empty the queue so we don't have to many motion activated 
            # scenes running
            while not self.queue.empty():
                self.queue.get_nowait()

async def main():
    queue = asyncio.Queue()
    scene = Scene(queue)
    await queue.put(True)
    await asyncio.create_task(scene.run())


if __name__ == "__main__":
    asyncio.run(main())
