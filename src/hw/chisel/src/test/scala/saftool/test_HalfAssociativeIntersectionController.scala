import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.flatspec.AnyFlatSpec

class Workload_HalfAssociativeIntersectionController_Random(dut: HalfAssociativeIntersectionController) extends PeekPokeTester(dut) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  // Canned values for tagMemoryInterface
  val cannedTagValues = Seq.fill(dut.numTags)(rand.nextInt(math.pow(2, dut.tagBitWidth).toInt))

  for (i <- 0 until 100) {
    val enableValue = if (i % 10 == 0) 0 else 1
    val triggerValue = rand.nextBoolean()
    val tagInputValue = rand.nextInt(math.pow(2, dut.tagBitWidth).toInt)
    val disableComparatorMaskValue = rand.nextInt(math.pow(2, dut.numTags).toInt)

    poke(dut.io.enable, enableValue)
    poke(dut.io.triggerInput, triggerValue)
    poke(dut.io.tagInput, tagInputValue)
    poke(dut.io.disableComparatorMask, disableComparatorMaskValue)

    // Poke canned values into tagMemoryInterface
    cannedTagValues.zipWithIndex.foreach { case (value, index) =>
      poke(dut.io.tagMemoryInterface(index), value)
    }

    step(1)
  }
}

class Test_Sim_HalfAssociativeIntersectionController extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "HalfAssociativeIntersectionController"
  it should "handle various inputs and enable states" in {
    test(new HalfAssociativeIntersectionController(numTags = 8, tagBitWidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_HalfAssociativeIntersectionController_Random(_))
  }
}
