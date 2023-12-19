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
  val enableAssertions = false // Flag to enable/disable assertions

  def createErrorMessage(expected: Any, actual: Any, inputs: Map[String, Any]): String = {
    val inputStr = inputs.map { case (key, value) => s"$key: $value" }.mkString(", ")
    s"Expected $expected, found $actual. Inputs: $inputStr"
  }

  reset(2)
  step(3)

  val cannedTagValues = Seq.fill(dut.numTags)(rand.nextInt(math.pow(2, dut.tagBitWidth).toInt))

  for (i <- 0 until 100) {
    val enableValue = rand.nextBoolean()
    val triggerValue = rand.nextBoolean()
    val disableComparatorMaskValue = rand.nextInt(math.pow(2, dut.numTags).toInt)
    val tagInputValue = rand.nextInt(math.pow(2, dut.tagBitWidth).toInt)
    val forcePeekValue = rand.nextBoolean()
    val headInValue = rand.nextInt(dut.numTags)

    poke(dut.io.enable, if (enableValue) 1 else 0)
    poke(dut.io.triggerInput, triggerValue)
    poke(dut.io.tagInput, tagInputValue)
    poke(dut.io.disableComparatorMask, disableComparatorMaskValue)
    poke(dut.io.force_peek, forcePeekValue)
    poke(dut.io.head_in, headInValue)

    val readAddress = if (peek(dut.io.memoryLookupEnable) == 1) peek(dut.io.memoryLookupAddress).toInt else 0
    val memReadValue = if (readAddress >= 0 && readAddress < cannedTagValues.length) cannedTagValues(readAddress) else 0
    poke(dut.io.memReadTag, memReadValue)

    cannedTagValues.zipWithIndex.foreach { case (value, index) =>
      poke(dut.io.tagMemoryInterface(index), value)
    }

    step(1)

    if (enableAssertions) {
      val inputs = Map(
        "enableValue" -> enableValue,
        "triggerValue" -> triggerValue,
        "disableComparatorMaskValue" -> disableComparatorMaskValue,
        "tagInputValue" -> tagInputValue,
        "forcePeekValue" -> forcePeekValue,
        "headInValue" -> headInValue,
        "readAddress" -> readAddress,
        "memReadValue" -> memReadValue
      )

      val expectedPeekOut = if (enableValue && forcePeekValue) cannedTagValues.lift(headInValue).getOrElse(0) else if (enableValue) memReadValue else 0

      val expectedHeadOut = if (enableValue && forcePeekValue) {
        headInValue + 1
      } else if (enableValue) {
        val index = cannedTagValues.indexWhere(_ >= tagInputValue)
        if (index >= 0 && index < dut.numTags) index else headInValue
      } else {
        headInValue
      }

      val expectedIsMatch = if (enableValue && !forcePeekValue) 1 else 0
      val expectedMemoryLookupEnable = if (enableValue && !forcePeekValue) 1 else 0
      val expectedMemoryLookupAddress = if (expectedMemoryLookupEnable == 1) readAddress else 0

      val expectedDisableNextStageMask = if (!enableValue) {
        0
      } else if (forcePeekValue) {
        disableComparatorMaskValue | (1 << headInValue)
      } else {
        disableComparatorMaskValue | (1 << expectedHeadOut)
      }

      assert(peek(dut.io.peek_out) == expectedPeekOut, createErrorMessage(expectedPeekOut, peek(dut.io.peek_out), inputs))
      assert(peek(dut.io.head_out) == expectedHeadOut, createErrorMessage(expectedHeadOut, peek(dut.io.head_out), inputs))
      assert(peek(dut.io.isMatch) == expectedIsMatch, createErrorMessage(expectedIsMatch, peek(dut.io.isMatch), inputs))
      assert(peek(dut.io.memoryLookupEnable) == expectedMemoryLookupEnable, createErrorMessage(expectedMemoryLookupEnable, peek(dut.io.memoryLookupEnable), inputs))
      assert(peek(dut.io.memoryLookupAddress) == expectedMemoryLookupAddress, createErrorMessage(expectedMemoryLookupAddress, peek(dut.io.memoryLookupAddress), inputs))
      assert(peek(dut.io.disableNextStageMask) == expectedDisableNextStageMask, createErrorMessage(expectedDisableNextStageMask, peek(dut.io.disableNextStageMask), inputs))
    }
  }
}

class Test_Sim_HalfAssociativeIntersectionController extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "HalfAssociativeIntersectionController"
  it should "handle various inputs and enable states" in {
    test(new HalfAssociativeIntersectionController(numTags = 8, tagBitWidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_HalfAssociativeIntersectionController_Random(_))
  }
}
